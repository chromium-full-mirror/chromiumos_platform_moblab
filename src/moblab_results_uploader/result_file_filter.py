# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test result filter example:

The filter is defined in YAML syntax. The syntax is:
    - suite_name_regex: SUITE_NAME_REGEX
      include:
          - FILE_OR_DIR_GLOB_PATTERN
          - ...
      exclude:
          - FILE_OR_DIR_GLOB_PATTERN
          - ...

Where:
    suite_name_regex: A regex to match which suite this filter applies to.
    include: Optional. The value is a list of glob pattern of files/dirs to be
        included. All files are included when omitted.
    exclude: Optional. The value is a list of glob patterns of files/dirs to be
        excluded. None file are excluded when omitted.

An example filter:
---
- suite_name_regex: ^cts|^gts:
  exclude:
    - debug/
    - cheets*/debug
"""
from __future__ import print_function

import asyncio
import collections
import fnmatch
import logging
import os
import pathlib
import re

import yaml
from os import path

import processing_step

_LOGGER = logging.getLogger("moblab_uploader")
UPLOADING_PROGRESS_FILENAME = "uploading_progress.txt"


class ResultFile(
    collections.namedtuple("ResultFile", ["test_result", "relative_path"])
):
    """A class to represent a file in a test result directory.
    It has two fields:
        test_result: is a TestResult object which this file belongs to.
        relative_path: the path relative to the test result directory.
    """

    @property
    def abs_path(self):
        return self.test_result.abs_path / self.relative_path

    def __str__(self):
        return str(self.abs_path)


class FilterConfigError(Exception):
    """Error raised when parse filter configurations."""


_KEY_SUITE_NAME_REGEX = "suite_name_regex"
_KEY_INCLUDE = "include"
_KEY_EXCLUDE = "exclude"


def _get_filter_by_suite(filters, suite_name):
    """Get the filter config for `suite_name` form `filters`."""
    if not suite_name:
        return None

    for filter in filters:
        regex = filter[_KEY_SUITE_NAME_REGEX]
        if re.match(regex, suite_name):
            return filter


async def _list_all_files(test_result, next_step):
    """List all files of `test_result` and pass to `next_step`."""
    for root, dirs, files in os.walk(test_result.abs_path):
        if not files:
            continue
        relative_root = pathlib.Path(root).relative_to(test_result.abs_path)
        for f in files:
            await next_step(
                ResultFile(
                    test_result=test_result,
                    relative_path=relative_root / f,
                )
            )


def filters_sanity_check(filters):
    """Sanity check for the filters."""
    for filter in filters:
        extra_key = set(filter.keys())
        extra_key -= {_KEY_SUITE_NAME_REGEX, _KEY_INCLUDE, _KEY_EXCLUDE}
        if extra_key:
            raise FilterConfigError(
                "Found extra key for filter {}: {}".format(filter, extra_key)
            )

        # _KEY_SUITE_NAME_REGEX is required.
        if _KEY_SUITE_NAME_REGEX not in filter:
            raise FilterConfigError(
                "Required key {} is missing from {}.".format(
                    _KEY_SUITE_NAME_REGEX, filter
                )
            )
        # The value of _KEY_INCLUDE and _KEY_EXCLUDE is a list.
        for key in [_KEY_INCLUDE, _KEY_EXCLUDE]:
            value = filter.get(key, [])
            if type(value) is not list:
                raise FilterConfigError(
                    "The '{}' value of {} is not a list.".format(key, filter)
                )


class ResultFileFilter(processing_step.ProcessStep):
    """A class to generate all files according to predefined filters.

    We only filter files when the test result succeeded.
    """

    def __init__(self, *, next_step=None, filter_config=None, force=False):
        """Constructor.

        Args:
            filter_config: A dict has all filter configurations.
            next_step: A coroutine to pass processed data to.
            force: True indicates to filter regardless the test succeeded or
                not.
        """
        self._filters_config = filter_config or {}
        self._applicable_filter = None
        self._force = force
        self._next_step = next_step

    async def _filter(self, result_file):
        """Check the file path with predefined filter patterns."""
        for pattern in self._applicable_filter.get(_KEY_INCLUDE, ["*"]):
            if fnmatch.fnmatch(str(result_file.relative_path), pattern):
                break
        else:
            return

        for pattern in self._applicable_filter.get(_KEY_EXCLUDE, []):
            if fnmatch.fnmatch(str(result_file.relative_path), pattern):
                return

        await self._next_step(result_file)

    async def list_all_files(self, test_result):
        """Generate all files of `test_result` and pass to `next_step`."""
        await _list_all_files(test_result, next_step=self._next_step)

    async def filter_files(self, test_result):
        """Filter files of `test_result` according to predefined filters."""
        if test_result.succeeded and test_result.skip_uploading_when_succeeded:
            return

        self._applicable_filter = _get_filter_by_suite(
            self._filters_config, test_result.suite_name
        )

        already_uploaded_files = self._load_uploaded_files(test_result)

        if not self._applicable_filter:
            _LOGGER.info(
                "No filter found for %s (%s). List all files then.",
                test_result,
                test_result.suite_name,
            )
            await _list_all_files(
                test_result,
                next_step=self._get_filter_uploaded_func(
                    already_uploaded_files, self._next_step
                ),
            )
            return

        if self._force or test_result.succeeded:
            _LOGGER.info(
                "Apply below filter to %s.\n%s",
                test_result,
                self._applicable_filter,
            )
            await _list_all_files(
                test_result,
                next_step=self._get_filter_uploaded_func(
                    already_uploaded_files, self._filter
                ),
            )
        else:
            await _list_all_files(
                test_result,
                next_step=self._get_filter_uploaded_func(
                    already_uploaded_files, self._next_step
                ),
            )

    def _get_filter_uploaded_func(
        self, already_uploaded_files, next_step_override
    ):
        """Creatres a funtion to filter already uploaded files.

        Args:
            already_uploaded_files: list of relative files paths.
            next_step_override: next function to call is case of

        Returns a results specific function to filter already uploaded files.
        """

        async def _filter_func(result_file):
            """Filter function of uploaded results.
            Captures already_uploaded_files and next_step_override.
            """
            if str(result_file.relative_path) not in already_uploaded_files:
                await next_step_override(result_file)
            else:
                _LOGGER.info(
                    "Skipping (%s), file has been already uploaded"
                    % result_file.relative_path
                )

        return _filter_func

    def _load_uploaded_files(self, test_result):
        """Fetches the list of already uploaded files for given test_result.
        Creates the file if it does not exist.

        Args:
            test_result: ResultAndStatus object representing the result.

        Return:
            The list of strings representing relative
            paths of already uploaded files.
        """
        file_path = test_result.abs_path / UPLOADING_PROGRESS_FILENAME

        _LOGGER.debug("Loading list of uploaded files %s", file_path)

        if not path.exists(file_path):
            self._create_fresh_uploading_progress_file(test_result)

        return set(line.strip() for line in open(file_path, "r"))

    def _create_fresh_uploading_progress_file(self, test_result):
        """Clears out the list of already uploaded files"""
        file_path = test_result.abs_path / UPLOADING_PROGRESS_FILENAME

        _LOGGER.debug("Creating file %s", file_path)
        with open(file_path, "w") as f:
            f.write("%s\n" % UPLOADING_PROGRESS_FILENAME)


def mark_files_uploaded(result_files):
    """Function that saves the progress of results upload

    Appends the result_files to uploading_progress.txt.

    Args:
        result_files: list of ResultFile objects of uploaded files
    """
    # Short circuit if nothing to mark
    if not result_files:
        return

    # Make sure all the files are for the same result
    result_dir = result_files[0].test_result.abs_path
    if any(rf.test_result.abs_path != result_dir for rf in result_files):
        _LOGGER.warning("Multiple results in one upload batch %s", result_dir)
        return

    file_path = result_dir / UPLOADING_PROGRESS_FILENAME
    if not path.exists(file_path):
        _LOGGER.warning(
            "%s file is not found in %s",
            UPLOADING_PROGRESS_FILENAME,
            result_dir,
        )

    with open(file_path, "a") as f:
        for uf in result_files:
            f.write("%s\n" % uf.relative_path)
