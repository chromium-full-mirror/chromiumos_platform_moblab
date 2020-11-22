# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for module `cmd_try_file_filter`."""

from __future__ import print_function

import argparse
import asyncio
import pathlib
from unittest import mock

import pytest

import test_result_registry
import cmd_try_file_filter

_TEST_RESULT_CLS = mock.Mock(GLOB_PATTERN="hosts/*-*")
test_result_registry.REGISTRY = [
    test_result_registry.TestResultRegisteryEntry(
        root_dir=pathlib.Path("/root"), classes=[_TEST_RESULT_CLS]
    )
]


def test_add_argument():
    """Test for command line options processing."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    cmd_try_file_filter.add_arguments(subparsers)
    args = parser.parse_args([cmd_try_file_filter.SUB_COMMAND_NAME, "-d", "."])
    assert args.dir.is_dir()
    assert args.dir.is_absolute()

    with pytest.raises(SystemExit):
        args = parser.parse_args(
            [cmd_try_file_filter.SUB_COMMAND_NAME, "-d", "some_nonexist_path"]
        )


def test_try_file_filter_cmd_wrong_input():
    """Test for returning error when input dir isn't a test result dir."""
    args = mock.Mock(dir=pathlib.Path("/path/to/results/123-moblab"))

    assert cmd_try_file_filter.try_file_filter(args) != 0

    args = mock.Mock(dir=pathlib.Path("/root/not-a-test-dir"))

    assert cmd_try_file_filter.try_file_filter(args) != 0


@mock.patch("os.walk")
def test_try_file_filter_cmd(m_walk):
    test_result_dir = "/root/hosts/123-moblab"
    m_walk.return_value = [[test_result_dir, (), ("file1", "file2")]]
    filter_config = [{"suite_name_regex": ".*"}]
    summary = (
        "Filtering result: {file_count} files: {file_size} bytes => "
        "{file_count} files: {file_size} bytes. 0% space saved!".format(
            file_count=2, file_size=2048
        )
    )
    args = mock.Mock(
        dir=pathlib.Path(test_result_dir),
        uploading_filter_config=filter_config,
        list_result_files=True,
    )
    test_result = _TEST_RESULT_CLS.return_value
    test_result.abs_path = pathlib.Path(test_result_dir)
    test_result.suite_name = "cts_P"
    test_result.skip_uploading_when_succeeded = False

    asyncio.set_event_loop(asyncio.new_event_loop())
    with mock.patch("cmd_try_file_filter._get_file_size") as m_get_size:
        m_get_size.return_value = 1024
        with mock.patch("cmd_try_file_filter.print", create=True) as m_print:
            cmd_try_file_filter.try_file_filter(args)
            m_print.assert_any_call(pathlib.PosixPath("file1"))
            m_print.assert_any_call(pathlib.PosixPath("file2"))
            m_print.assert_any_call(summary)
