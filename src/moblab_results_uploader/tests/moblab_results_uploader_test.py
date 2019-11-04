# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for `moblab_results_uploader`."""

from __future__ import print_function

import asyncio
import collections
import datetime
import enum
import functools
import pathlib
import re
import shutil
import tempfile
import unittest
from unittest import mock

import pytest

import autotest_result
import cmd_run
import moblab_results_uploader
import result_dir_status
import test_result_registry

_EXPIRED = result_dir_status.Status.EXPIRED
_UPLOADED = result_dir_status.Status.UPLOADED
_UPLOADING = result_dir_status.Status.UPLOADING
_CTS = 'cts_P'
_FILTER_CONFIG = [
    {'suite_name_regex': 'cts', 'exclude': ['*/debug/*']}
]

TYPE = enum.Enum('TYPE', ['JOB', 'TASK'])
FakeDir = collections.namedtuple(
    'FakeDir', ['id', 'type', 'finished_time', 'status_dot_log',
                'uploading_status', 'suite_name'])

# For result id in [10, 20), they will be removed.
# For result id in [20, 30), the will be uploaded and leave on disk.
# For result >= 30, we will just leave it on local disk.
_DIRECTORIES = [
    # Expired results. Will be removed.
    FakeDir(10, TYPE.JOB, '2020-01-01 00:00:00', 'FAIL', _EXPIRED, ''),
    FakeDir(11, TYPE.TASK, '2020-01-01 00:30:00', 'GOOD', _EXPIRED, ''),
    # Uploaded but expired results. Will be removed.
    FakeDir(12, TYPE.JOB, '2020-01-01 00:40:00', 'GOOD', _UPLOADED, ''),
    FakeDir(13, TYPE.TASK, '2020-01-01 00:40:00', 'GOOD', _UPLOADED, ''),
    # Incomplete but expired results. Will be removed.
    FakeDir(14, TYPE.JOB, '2020-01-01 01:40:00', 'GOOD', _UPLOADED, ''),
    FakeDir(15, TYPE.TASK, '2020-01-01 01:40:00', 'GOOD', _UPLOADED, ''),
    # Incomplete and expired results. Will be removed.
    # FIXME
    # FakeDir(16, TYPE.JOB, '2020-01-01 01:40:00', 'GOOD', _UPLOADING, ''),
    # FakeDir(17, TYPE.TASK, '2020-01-01 01:40:00', 'GOOD', _UPLOADING, ''),
    # Incomplete and not expired yet results. Will be uploaded.
    FakeDir(20, TYPE.JOB, '2020-01-06 01:40:00', 'GOOD', _UPLOADING, ''),
    FakeDir(21, TYPE.TASK, '2020-01-06 01:40:00', 'GOOD', _UPLOADING, ''),
    FakeDir(22, TYPE.JOB, '2020-01-06 01:40:00', 'GOOD', _UPLOADING, _CTS),
    FakeDir(23, TYPE.TASK, '2020-01-06 01:40:00', 'GOOD', _UPLOADING, ''),
    FakeDir(24, TYPE.JOB, '2020-01-06 01:40:00', 'FAIL', _UPLOADING, _CTS),
    FakeDir(25, TYPE.TASK, '2020-01-06 01:40:00', 'ABORT', _UPLOADING, ''),
    # Uploaded and not expired results. Will not touch.
    FakeDir(30, TYPE.JOB, '2020-01-06 00:40:00', 'GOOD', _UPLOADED, ''),
    FakeDir(31, TYPE.TASK, '2020-01-06 00:40:00', 'GOOD', _UPLOADED, ''),
    # Still running results. Will not touch.
    FakeDir(42, TYPE.JOB, None, None, None, None,),
    FakeDir(43, TYPE.TASK, None, None, None, None),
    # TODO(guocb) Add testing for timing out.
]


def get_finished_time(id_list, *, query_type):
    id_ = id_list[0]
    key = 'created_on' if query_type == TYPE.JOB else 'time_finished'
    for result_dir_obj in _DIRECTORIES:
        if int(id_) == result_dir_obj.id and result_dir_obj.finished_time:
            return [{key: result_dir_obj.finished_time}]

    return [{}]


def prepare_dir(root_dir, result_dir_obj, job_serialize_CTS):
    if result_dir_obj.type == TYPE.JOB:
        result_dir = root_dir / '{}-moblab/foo'.format(result_dir_obj.id)
        top_dir = result_dir.parent
    else:
        result_dir = root_dir / 'hosts/foo/{}-task'.format(result_dir_obj.id)
        top_dir = result_dir
    result_dir.mkdir(parents=True, exist_ok=True)
    for subdir in ('.', 'debug', 'sysinfo'):
        (result_dir / subdir).mkdir(exist_ok=True)
        for f in ('file1', 'file2', 'file3'):
            with (result_dir / subdir / f).open('w') as fd:
                fd.write('some test\ndata.')

    if result_dir_obj.status_dot_log:
        # Create fake status.log.
        # pylint: disable=protected-access
        with (result_dir / autotest_result._STATUS_LOG).open('w') as f:
            f.write('END {}'.format(result_dir_obj.status_dot_log))

    if result_dir_obj.uploading_status:
        with (top_dir / result_dir_status.MARKER_FILE).open('w') as f:
            f.write(result_dir_obj.uploading_status.name)

    if result_dir_obj.type == TYPE.JOB:
        with (result_dir / autotest_result._JOB_INFO).open('wb') as f:
            if result_dir_obj.suite_name == _CTS:
                f.write(job_serialize_CTS)

            else:
                f.write(b'')


@pytest.yield_fixture
def temp_root_dir(job_serialize_CTS):
    """Create a temp dir and some mock directories."""
    root_dir = pathlib.Path(tempfile.mkdtemp())
    for result_dir_obj in _DIRECTORIES:
        prepare_dir(root_dir, result_dir_obj, job_serialize_CTS)
    yield root_dir
    shutil.rmtree(root_dir, ignore_errors=True)


@mock.patch('cmd_run.add_arguments', new=mock.Mock)
@mock.patch('cmd_try_file_filter.add_arguments', new=mock.Mock)
def test_main__no_subcommand():
    with pytest.raises(SystemExit):
        moblab_results_uploader.main([])


@mock.patch('cmd_run.add_arguments', new=mock.Mock)
@mock.patch('cmd_try_file_filter.add_arguments', new=mock.Mock)
@mock.patch('moblab_results_uploader.hasattr', new=mock.Mock)
def test_main__logger_file_option():
    with pytest.raises(AttributeError):
        moblab_results_uploader.main(
            ['-l', '/tmp/moblab_result_uploader.log'])

    with pytest.raises(SystemExit):
        moblab_results_uploader.main(
            ['-l', '/cannot-create-log-here'])


@mock.patch('cmd_run.add_arguments', new=mock.Mock)
@mock.patch('cmd_try_file_filter.add_arguments', new=mock.Mock)
@mock.patch('moblab_results_uploader.hasattr', new=mock.Mock)
def test_main__config_filter_option():
    with pytest.raises(AttributeError):
        moblab_results_uploader.main([])

    with pytest.raises(SystemExit):
        moblab_results_uploader.main(['-f', '/non-exist-file'])

    with tempfile.NamedTemporaryFile() as tmp_file:
        with pytest.raises(AttributeError):
            tmp_file.write(b'---\n')
            tmp_file.seek(0)
            moblab_results_uploader.main(['-f', tmp_file.name])

    with tempfile.NamedTemporaryFile() as tmp_file:
        with pytest.raises(SystemExit):
            tmp_file.write(b'---\n- abc: def\n')
            tmp_file.seek(0)
            moblab_results_uploader.main(['-f', tmp_file.name])


@pytest.yield_fixture
def afe():
    with mock.patch('moblab_common.afe_connector.AFEConnector') as m_AFE:
        _afe = m_AFE.return_value
        _afe.get_jobs.side_effect = functools.partial(get_finished_time,
                                                      query_type=TYPE.JOB)
        _afe.get_special_tasks.side_effect = functools.partial(
            get_finished_time, query_type=TYPE.TASK)
        _afe.get_host_queue_entries.return_value = None
        yield _afe


def build_registry(temp_root_dir):
    return [
        test_result_registry.TestResultRegisteryEntry(
            root_dir=temp_root_dir,
            classes=[
                autotest_result.AutotestTestJob,
                autotest_result.AutotestHostTask
            ]
        )
    ]


@mock.patch('google.cloud.storage.Client')
@mock.patch.object(datetime, 'datetime', wraps=datetime.datetime)
def test_run_once(m_datetime, m_gs_api, afe, temp_root_dir):
    m_datetime.now.return_value = datetime.datetime(2020, 1, 10)

    args = mock.Mock(once=True, credentials_file='cred', jobs=3,
                     min_age_to_upload=datetime.timedelta(days=1),
                     min_age_to_prune=datetime.timedelta(days=7),
                     upload_timeout=datetime.timedelta(days=3),
                     uploading_filter_config=_FILTER_CONFIG)

    asyncio.set_event_loop(asyncio.new_event_loop())
    cmd_run.run(args, test_result_registry=build_registry(temp_root_dir))

    blob = m_gs_api.return_value.get_bucket.return_value.blob
    uploaded_files = [call[0][0] for call in blob.call_args_list]
    for f in uploaded_files:
        assert re.match(
            r'results/[^/]+/[0-9a-f]{32}/(2\d-moblab|hosts/foo/2\d-task)/.*',
            f
        )
        # The job of 22 are CTS and succeeded, so no debug data uploaded.
        assert not re.match(
            r'results/[^/]+/[0-9a-f]{32}/22-moblab/foo/debug/', f)

    # The job of 24 are CTS but failed, so all files will be uploaded.
    assert [f for f in uploaded_files if re.match(
        r'results/[^/]+/[0-9a-f]{32}/24-moblab/foo/debug', f
    )]

    # All dir with id in [10, 20) should be removed.
    assert [d for d in temp_root_dir.glob('1*-moblab')] == []
    assert [d for d in temp_root_dir.glob('hosts/foo/1*-task')] == []
    # All dir with id in [20,) should be left on disk.
    for id_ in ['2*', '3*', '4*']:
        assert list(temp_root_dir.glob('{}-moblab'.format(id_))) != []
        assert list(temp_root_dir.glob(
            'hosts/foo/{}-task'.format(id_))) != []


@pytest.mark.network
@mock.patch.object(datetime, 'datetime', wraps=datetime.datetime)
def test_integration_test(m_datetime, afe, temp_root_dir, gs_bucket,
                          credentials_file):
    m_datetime.now.return_value = datetime.datetime(2020, 1, 10)

    args = mock.Mock(
        once=True, gs_bucket=gs_bucket, credentials_file=credentials_file,
        jobs=3, uploading_filter_config=_FILTER_CONFIG,
        min_age_to_upload=datetime.timedelta(days=1),
        min_age_to_prune=datetime.timedelta(days=7),
        upload_timeout=datetime.timedelta(days=3)
    )

    asyncio.set_event_loop(asyncio.new_event_loop())
    cmd_run.run(args, test_result_registry=build_registry(temp_root_dir))

    # TODO(guocb) Automatically verify the uploaded results.
