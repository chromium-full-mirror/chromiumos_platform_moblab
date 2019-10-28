# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A subcommand to try the file filter locally with a test result directory.

This subcommand prints a summary of the total file count and size of
before/after applying the filter.

Optionally, it prints out the filtered file list.
"""
from __future__ import print_function

import argparse
import asyncio
import logging
import pathlib

import processing_step
import result_file_filter
import test_result_registry

SUB_COMMAND_NAME = 'try_filter'

_LOGGER = logging.getLogger(pathlib.Path(__file__).stem)
_RC_NO_MATCHED_CLASS = 1
_PRINT_FILE_LIST_LIMIT = 100


def _directory_type(path):
    """Check `path` wrap it with a pathlib.Path object.

    We convert input `path` to a abs path in order to help following steps.
    """
    path = pathlib.Path(path)

    # Convert relative path to abs path if needed. Don't use
    # pathlib.Path.resolve here because it also follows symlink which may
    # confuse selecting proper test result class.
    if not path.is_absolute():
        path = pathlib.Path(path).resolve()

    if path.is_dir():
        return path
    raise argparse.ArgumentTypeError('Invalid directory name: {}'.format(path))


def _get_file_size(result_file):
    """Get the size of a file."""
    return result_file.abs_path.lstat().st_size


def _create_test_result_obj(abs_path, registry=None):
    """Create test result object for `path` according to test result registry.

    Args:
        abs_path: A pathlib.Path object with abs path name.
        registry: A dict has all test result class registered.
    """
    for registry_entry in registry or test_result_registry.REGISTRY:
        root_dir = registry_entry.root_dir
        for parent in abs_path.parents:
            if parent == root_dir:
                break
        else:
            continue
        for cls in registry_entry.classes:
            if abs_path.match(str(root_dir / cls.GLOB_PATTERN)):
                return cls(root_dir=root_dir,
                           relative_path=abs_path.relative_to(root_dir))


class _Counter(processing_step.ProcessStep):
    """A counter coroutine which count input."""

    def __init__(self, *, method=None, next_step=None):
        """Constructor.

        Args:
            method: A func which count input and return an integer to be added
            to total sum. Default is just return 1.
            next_step: The following coroutine in the whole processing pipeline.
        """
        super().__init__(next_step=next_step)
        self._sum = 0
        self._method = method or (lambda _: 1)

    @property
    def sum(self):
        """Return the count result."""
        return self._sum

    def reset(self):
        """Reset the counter."""
        self._sum = 0

    async def count(self, data):
        """A coroutine to count input and sum the result."""
        self._sum += self._method(data)
        if self._next_step:
            await self._next_step(data)


class _FileNamePrinter(processing_step.ProcessStep):
    """A configurable class to print input file name."""

    def __init__(self, *, next_step=None, limit=0):
        super().__init__(next_step=next_step)
        self._limit = limit
        self._count = 0
        _LOGGER.info('The filtered files will be listed, but up to %s files.',
                     limit)

    async def print(self, result_file):
        if self._limit:
            self._count += 1
        if self._count > self._limit:
            return
        print(result_file.relative_path)


def add_arguments(parent_parser):
    """Add arguments for this subcommand.

    Args:
        parent_parser: The argparse.ArgumentParser object to add arguments.
    """
    parser = parent_parser.add_parser(
        SUB_COMMAND_NAME,
        help='Try the file filter locally with a real test result directory '
        'and see the filtering result.')
    parser.add_argument(
        '-d', '--dir', type=_directory_type, required=True,
        help='The directory to test the file filter.'
    )
    parser.add_argument(
        '-l', '--list-result-files', action='store_true',
        help='Print out all the files after applying the filter.'
    )

    parser.set_defaults(func=try_file_filter)


def try_file_filter(args):
    test_result = _create_test_result_obj(args.dir)
    if not test_result:
        _LOGGER.error('No registered class matches the directory: %s', args.dir)
        return _RC_NO_MATCHED_CLASS

    files_generator = result_file_filter.ResultFileFilter(
        filter_config=args.uploading_filter_config, force=True)
    file_counter = _Counter()
    file_size_counter = _Counter(method=_get_file_size)

    # The process steps:
    # generate file list -> optionally filter them -> count file
    #       -> count file size -> optionally print the file name.
    files_generator.next_step = file_counter.count
    file_counter.next_step = file_size_counter.count

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(files_generator.list_all_files(test_result))

        total_file_count = file_counter.sum
        total_file_size = file_size_counter.sum

        # Reset counters for counting filtered files.
        file_counter.reset()
        file_size_counter.reset()

        if args.list_result_files:
            file_size_counter.next_step = _FileNamePrinter(
                limit=_PRINT_FILE_LIST_LIMIT).print

        loop.run_until_complete(files_generator.filter_files(test_result))
    finally:
        loop.close()

    filtered_file_count = file_counter.sum
    filtered_file_size = file_size_counter.sum

    print('Filtering result: {} files: {} bytes => {} files: {} bytes'.format(
        total_file_count, total_file_size,
        filtered_file_count, filtered_file_size
    ))
    return 0
