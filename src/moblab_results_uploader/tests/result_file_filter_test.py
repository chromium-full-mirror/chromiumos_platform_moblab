# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for `result_file_filter`."""
from __future__ import print_function

import asyncio
import pathlib
from asynctest import mock

import pytest
import yaml

import result_file_filter

_MOCK_FILE_SYSTEM = [
    ('/root/result', ('dir1', 'dir2', 'empty', 'debug'), ('file1', 'file2')),
    ('/root/result/dir1', (), ('file3',)),
    ('/root/result/dir2', (), ('file4', 'file5')),
    ('/root/result/empty', (), ()),
    ('/root/result/debug', (), ('dump1', 'dump2')),
]

_FILTER_CONFIG = '''
---
- suite_name_regex: suite1
  exclude:
  - debug/*

- suite_name_regex: suite2
  include:
    - dir2/*
  exclude:
    - dir2/file5
'''


@pytest.fixture
def filter_config():
    return yaml.load(_FILTER_CONFIG, Loader=yaml.BaseLoader)


def _count_total_file():
    return sum(len(files) for *_, files in _MOCK_FILE_SYSTEM)


@pytest.mark.asyncio
@mock.patch('os.walk')
async def test_list_all_files(m_walk, next_step):
    m_walk.return_value = _MOCK_FILE_SYSTEM
    test_result = mock.Mock(abs_path='/root/result', succeeded=True)
    filter = result_file_filter.ResultFileFilter(next_step=next_step)
    await filter.list_all_files(test_result)

    assert next_step.await_count == _count_total_file()


@pytest.mark.asyncio
@mock.patch('os.walk')
async def test_filter_files(m_walk, filter_config, next_step):
    m_walk.return_value = _MOCK_FILE_SYSTEM
    test_result = mock.Mock(abs_path='/root/result', succeeded=True)
    filter = result_file_filter.ResultFileFilter(filter_config=filter_config,
                                                 next_step=next_step)
    with mock.patch('result_file_filter._get_test_suite',
                    return_value='suite1'):
        await filter.filter_files(test_result)

    # 2 files in debug directory.
    assert next_step.await_count == _count_total_file() - 2


@pytest.mark.asyncio
@mock.patch('os.walk')
async def test_filter_files_not_in_config(m_walk, filter_config, next_step):
    """Test filtering of a suite not configured in config file."""
    m_walk.return_value = _MOCK_FILE_SYSTEM
    test_result = mock.Mock(abs_path='/root/result')
    filter = result_file_filter.ResultFileFilter(filter_config=filter_config,
                                                 next_step=next_step)
    with mock.patch('result_file_filter._get_test_suite',
                    return_value='suite_not_configured'):
        await filter.filter_files(test_result)

    # We don't filter suite that not configured.
    assert next_step.await_count == _count_total_file()


@pytest.mark.asyncio
@mock.patch('os.walk')
async def test_filter_files_overlap(m_walk, filter_config, next_step):
    """Test filter configuration that has overlap in INCLUDE and EXCLUDE."""
    m_walk.return_value = _MOCK_FILE_SYSTEM
    test_result = mock.Mock(abs_path='/root/result')
    filter = result_file_filter.ResultFileFilter(filter_config=filter_config,
                                                 next_step=next_step)
    with mock.patch('result_file_filter._get_test_suite',
                    return_value='suite2'):
        await filter.filter_files(test_result)

    assert next_step.await_count == 1


@pytest.mark.asyncio
@mock.patch('os.walk')
async def test_filter_files_failed_test(m_walk, filter_config, next_step):
    """Test that we don't filter failed test result directory."""
    m_walk.return_value = _MOCK_FILE_SYSTEM
    test_result = mock.Mock(abs_path='/root/result', succeeded=False)
    filter = result_file_filter.ResultFileFilter(filter_config=filter_config,
                                                 next_step=next_step)
    with mock.patch('result_file_filter._get_test_suite',
                    return_value='suite2'):
        await filter.filter_files(test_result)

    assert next_step.await_count == _count_total_file()


@pytest.mark.asyncio
@mock.patch('os.walk')
async def test_filter_files_by_force(m_walk, filter_config, next_step):
    """Test that we don't check succeeded flag when filter by force."""
    m_walk.return_value = _MOCK_FILE_SYSTEM
    test_result = mock.Mock(abs_path='/root/result', succeeded=False)
    filter = result_file_filter.ResultFileFilter(filter_config=filter_config,
                                                 next_step=next_step,
                                                 force=True)
    with mock.patch('result_file_filter._get_test_suite',
                    return_value='suite2'):
        await filter.filter_files(test_result)

    assert next_step.await_count == 1


def test_filtesr_santiy_check_extra_key():
    config = [{'extra_key': ''}]
    with pytest.raises(result_file_filter.FilterConfigError):
        result_file_filter.filters_sanity_check(config)


def test_filtesr_santiy_check_missing_suite_name():
    config = [{'include': ''}]
    with pytest.raises(result_file_filter.FilterConfigError):
        result_file_filter.filters_sanity_check(config)


def test_filtesr_santiy_check_dir_should_be_a_list():
    config = [{'suite_name_regex': '.*', 'include': ''}]
    with pytest.raises(result_file_filter.FilterConfigError):
        result_file_filter.filters_sanity_check(config)


def test_result_file():
    test_result = mock.Mock()
    test_result.abs_path = pathlib.Path('/path/to/dir')
    result_file = result_file_filter.ResultFile(test_result=test_result,
                                                relative_path='path/to/file')
    assert str(result_file) == '/path/to/dir/path/to/file'
