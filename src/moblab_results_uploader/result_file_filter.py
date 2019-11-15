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

import processing_step

_LOGGER = logging.getLogger(pathlib.Path(__file__).stem)


class ResultFile(collections.namedtuple('ResultFile', ['test_result',
                                                       'relative_path'])):
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


_KEY_SUITE_NAME_REGEX = 'suite_name_regex'
_KEY_INCLUDE = 'include'
_KEY_EXCLUDE = 'exclude'


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
                ResultFile(test_result=test_result,
                           relative_path=relative_root / f)
            )


def filters_sanity_check(filters):
    """Sanity check for the filters."""
    for filter in filters:
        extra_key = set(filter.keys())
        extra_key -= {_KEY_SUITE_NAME_REGEX, _KEY_INCLUDE, _KEY_EXCLUDE}
        if extra_key:
            raise FilterConfigError(
                'Found extra key for filter {}: {}'.format(filter, extra_key))

        # _KEY_SUITE_NAME_REGEX is required.
        if _KEY_SUITE_NAME_REGEX not in filter:
            raise FilterConfigError(
                'Required key {} is missing from {}.'.format(
                    _KEY_SUITE_NAME_REGEX, filter))
        # The value of _KEY_INCLUDE and _KEY_EXCLUDE is a list.
        for key in [_KEY_INCLUDE, _KEY_EXCLUDE]:
            value = filter.get(key, [])
            if type(value) is not list:
                raise FilterConfigError(
                    "The '{}' value of {} is not a list.".format(key, filter))


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
        for pattern in self._applicable_filter.get(_KEY_INCLUDE, ['*']):
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
        self._applicable_filter = _get_filter_by_suite(self._filters_config,
                                                       test_result.suite_name)

        if not self._applicable_filter:
            _LOGGER.info('No filter found for %s (%s). List all files then.',
                         test_result, test_result.suite_name)
            await _list_all_files(test_result, next_step=self._next_step)
            return

        if self._force or test_result.succeeded:
            _LOGGER.info('Apply below filter to %s.\n%s', test_result,
                         self._applicable_filter)
            await _list_all_files(test_result, next_step=self._filter)
        else:
            await _list_all_files(test_result, next_step=self._next_step)
