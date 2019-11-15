# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for module `result_dir_status`."""

from __future__ import print_function

import asyncio
import datetime
import pathlib
import unittest
from asynctest import mock

import pytest

import result_dir_status
import test_result_interface

_MIN_AGE_TO_UPLOAD = datetime.timedelta(days=1)
_MIN_AGE_TO_PRUNE = datetime.timedelta(days=5)
_FINISHED_TIME = datetime.datetime(2020, 1, 1)
_HALF_DAY = datetime.timedelta(hours=12)


@pytest.fixture
def status_checker(next_step):
    return result_dir_status.ResultStatusChecker(
        min_age_to_upload=_MIN_AGE_TO_UPLOAD,
        min_age_to_prune=_MIN_AGE_TO_PRUNE,
        next_step=next_step)


@pytest.mark.asyncio
async def test_status_filter(next_step):
    status_filter = result_dir_status.StatusFilter(1, 2, next_step=next_step)
    result_and_status = mock.Mock(status=0)
    await status_filter.filter(result_and_status)
    next_step.assert_not_awaited()

    result_and_status = mock.Mock(status=2, test_result='data')
    await status_filter.filter(result_and_status)
    next_step.assert_awaited_once_with('data')


@pytest.mark.asyncio
async def test_result_status_checker__not_ready(next_step, status_checker):
    test_result = mock.Mock(finished_time=None, abs_path=pathlib.Path('/'))
    with mock.patch('moblab_common.lock_util.file_lock'):
        with mock.patch('pathlib.Path.open') as m_open:
            m_open.side_effect = FileNotFoundError
            await status_checker.check(test_result)
    next_step.assert_not_awaited()


@pytest.mark.asyncio
@mock.patch('moblab_common.lock_util.file_lock')
@mock.patch('pathlib.Path.open')
async def test_checker__expired_cannot_get_finished_time(
    m_open, m_lock, next_step, status_checker
):
    test_result = mock.Mock(abs_path=pathlib.Path('/'))
    type(test_result).finished_time = mock.PropertyMock(
        side_effect=test_result_interface.TestResultError)
    await status_checker.check(test_result)
    next_step.assert_awaited()


@pytest.mark.asyncio
@mock.patch('moblab_common.lock_util.file_lock')
@mock.patch('pathlib.Path.open')
async def test_checker__finished_but_not_ready(m_open, m_lock, next_step,
                                               status_checker):
    m_open.side_effect = FileNotFoundError

    now = _FINISHED_TIME + datetime.timedelta(hours=12)
    test_result = mock.Mock(finished_time=_FINISHED_TIME,
                            abs_path=pathlib.Path('/'))
    await status_checker.check(test_result)

    next_step.assert_not_awaited()


@pytest.mark.asyncio
@mock.patch('moblab_common.lock_util.file_lock')
@mock.patch('pathlib.Path.open')
async def test_checker__finished_and_expired(m_open, m_lock, next_step,
                                             status_checker):
    now = _FINISHED_TIME + _MIN_AGE_TO_PRUNE + _HALF_DAY

    test_result = mock.Mock(finished_time=_FINISHED_TIME,
                            abs_path=pathlib.Path('/'))
    with mock.patch.object(datetime, 'datetime') as m_datetime:
        m_datetime.now.return_value = now
        await status_checker.check(test_result)

    next_step.assert_awaited_once(status=result_dir_status.Status.EXPIRED,
                                  test_result=test_result)


@pytest.mark.asyncio
@mock.patch('moblab_common.lock_util.file_lock')
async def test_checker__to_expired(m_lock, next_step, status_checker):
    for status in [result_dir_status.Status.READY,
                   result_dir_status.Status.UPLOADED]:
        with mock.patch('pathlib.Path') as m_path:
            m_path.return_value.read_text.return_value = status.name
            now = _FINISHED_TIME + _MIN_AGE_TO_PRUNE + _HALF_DAY

            test_result = mock.Mock(finished_time=_FINISHED_TIME,
                                    abs_path=pathlib.Path('/'))
            with mock.patch.object(datetime, 'datetime') as m_datetime:
                m_datetime.now.return_value = now
                await status_checker.check(test_result)

            next_step.assert_awaited_once(
                status=result_dir_status.Status.EXPIRED,
                test_result=test_result)
            next_step.reset_mock()


@pytest.mark.asyncio
@mock.patch('moblab_common.lock_util.file_lock')
@mock.patch('pathlib.Path.open')
async def test_checker__to_uploading(m_open, m_lock, next_step,
                                     status_checker):
    now = _FINISHED_TIME + _MIN_AGE_TO_PRUNE - _HALF_DAY

    test_result = mock.Mock(finished_time=_FINISHED_TIME,
                            abs_path=pathlib.Path('/'))
    with mock.patch.object(datetime, 'datetime') as m_datetime:
        m_datetime.now.return_value = now
        await status_checker.check(test_result)

    next_step.assert_awaited_once(status=result_dir_status.Status.UPLOADING,
                                  test_result=test_result)
