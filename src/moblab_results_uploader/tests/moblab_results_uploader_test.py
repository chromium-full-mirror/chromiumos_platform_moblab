# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for `moblab_results_uploader`."""

from __future__ import print_function

import asyncio
import datetime
import pathlib
import shutil
import tempfile
import unittest
from unittest import mock

import autotest_result
import cmd_run
import moblab_results_uploader
import test_result_registry

_EXPIRED = result_dir_status.Status.EXPIRED
_UPLOADED = result_dir_status.Status.UPLOADED
_UPLOADING = result_dir_status.Status.UPLOADING
_CTS = 'cts_P'

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
    # Incomplete and not expired yet results. Will be uploaded.
    FakeDir(20, TYPE.JOB, '2020-01-06 01:40:00', 'GOOD', _UPLOADING, ''),
    FakeDir(21, TYPE.JOB, '2020-01-06 01:40:00', 'GOOD', _UPLOADING, _CTS,),
    FakeDir(22, TYPE.TASK, '2020-01-06 01:40:00', 'GOOD', _UPLOADING, ''),
    # Uploaded and not expired results. Will not touch.
    FakeDir(30, TYPE.JOB, '2020-01-06 00:40:00', 'GOOD', _UPLOADED, ''),
    FakeDir(31, TYPE.TASK, '2020-01-06 00:40:00', 'GOOD', _UPLOADED, ''),
    # Still running results. Will not touch.
    FakeDir(32, TYPE.JOB, None, None, None, None,),
    FakeDir(33, TYPE.TASK, None, None, None, None),
]


def afe_get_jobs_side_effect(id_list):
    id_ = id_list[0]
    for job, (finished_time, _) in _JOB_RESULT_DIR:
        if '{}-'.format(id_) in job:
            if not finished_time:
                return [{}]
            return [{'created_on': finished_time}]
    return [{}]


def afe_get_task_side_effect(id_list):
    id_ = id_list[0]
    for job, (finished_time, _) in _TASK_RESULT_DIR:
        if '{}-'.format(id_) in job:
            if not finished_time:
                return [{}]
            return [{'time_finished': finished_time}]
    return [{}]


def prepare_dir(dir_name, status_line):
    dir_name.mkdir(parents=True, exist_ok=True)
    for subdir in ('debug', 'sysinfo'):
        (dir_name / subdir).mkdir(exist_ok=True)
        for f in ('file1', 'file2', 'file3'):
            with (dir_name / subdir / f).open('w') as fd:
                fd.write('some test\ndata.')

    if status_line:
        # Create fake status.log.
        # pylint: disable=protected-access
        with (dir_name / autotest_result._STATUS_LOG).open('w') as f:
            f.write(status_line)

    if result_dir_obj.uploading_status:
        with (result_dir / result_dir_status.MARKER_FILE).open('w') as f:
            f.write(result_dir_obj.uploading_status.name)

class RestultUploaderTest(unittest.TestCase):
    """Unit test case for `test_result_uploader`."""

    def setUp(self):
        """Create a temp dir and some mock directories."""
        self.root_dir = pathlib.Path(tempfile.mkdtemp())
        for d, (_, status) in _JOB_RESULT_DIR + _TASK_RESULT_DIR:
            prepare_dir(self.root_dir / d, status)

    def tearDown(self):
        """Remove the test directory."""
        shutil.rmtree(self.root_dir, ignore_errors=True)

    @mock.patch('cmd_run.add_arguments', new=mock.Mock)
    @mock.patch('cmd_try_file_filter.add_arguments', new=mock.Mock)
    def test_main__no_subcommand(self):
        with self.assertRaises(SystemExit):
            moblab_results_uploader.main([])

    @mock.patch('cmd_run.add_arguments', new=mock.Mock)
    @mock.patch('cmd_try_file_filter.add_arguments', new=mock.Mock)
    @mock.patch('moblab_results_uploader.hasattr', new=mock.Mock)
    def test_main__logger_file_option(self):
        with self.assertRaises(AttributeError):
            moblab_results_uploader.main(
                ['-l', '/tmp/moblab_result_uploader.log'])

        with self.assertRaises(SystemExit):
            moblab_results_uploader.main(
                ['-l', '/cannot-create-log-here'])

    @mock.patch('cmd_run.add_arguments', new=mock.Mock)
    @mock.patch('cmd_try_file_filter.add_arguments', new=mock.Mock)
    @mock.patch('moblab_results_uploader.hasattr', new=mock.Mock)
    def test_main__config_filter_option(self):
        with self.assertRaises(AttributeError):
            moblab_results_uploader.main([])

        with self.assertRaises(SystemExit):
            moblab_results_uploader.main(['-f', '/non-exist-file'])

        with tempfile.NamedTemporaryFile() as tmp_file:
            with self.assertRaises(AttributeError):
                tmp_file.write(b'---\n')
                tmp_file.seek(0)
                moblab_results_uploader.main(['-f', tmp_file.name])

        with tempfile.NamedTemporaryFile() as tmp_file:
            with self.assertRaises(SystemExit):
                tmp_file.write(b'---\n- abc: def\n')
                tmp_file.seek(0)
                moblab_results_uploader.main(['-f', tmp_file.name])

    @mock.patch('google.cloud.storage.Client')
    @mock.patch('moblab_common.afe_connector.AFEConnector')
    @mock.patch.object(datetime, 'datetime', wraps=datetime.datetime)
    def test_run_once(self, m_datetime, m_AFE, m_gs_api):
        afe = m_AFE.return_value
        afe.get_jobs.side_effect = afe_get_jobs_side_effect
        afe.get_special_tasks.side_effect = afe_get_task_side_effect
        afe.get_host_queue_entries.return_value = None

        m_datetime.now.return_value = datetime.datetime(2020, 1, 10)

        args = mock.Mock(once=True, credentials_file='cred', jobs=3,
                         min_age_to_upload=datetime.timedelta(days=1),
                         min_age_to_prune=datetime.timedelta(days=7),
                         uploading_filter_config=[])
        args.upload_timeout = datetime.timedelta(days=3)

        registry = [
            test_result_registry.TestResultRegisteryEntry(
                root_dir=self.root_dir,
                classes=[
                    autotest_result.AutotestTestJob,
                    autotest_result.AutotestHostTask
                ]
            )
        ]
        asyncio.set_event_loop(asyncio.new_event_loop())
        cmd_run.run(args, test_result_registry=registry)
        print(m_gs_api.return_value.get_bucket.return_value.blob.call_args_list)
        # All dir with id in [10, 20) should be removed.
        assert [d for d in self.root_dir.glob('1*-moblab')] == []
        assert [d for d in self.root_dir.glob('hosts/foo/1*-task')] == []
        # All dir with id in [20,) should be left on disk.
        assert [d for d in self.root_dir.glob('2*-moblab')] != []
        assert [d for d in self.root_dir.glob('3*-moblab')] != []
        assert [d for d in self.root_dir.glob('hosts/foo/2*-task')] != []
        assert [d for d in self.root_dir.glob('hosts/foo/3*-task')] != []
