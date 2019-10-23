# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for `moblab_results_uploader`."""

from __future__ import print_function

import datetime
import pathlib
import shutil
import tempfile
import unittest

from unittest import mock

import autotest_result
import moblab_results_uploader


_JOB_RESULT_DIR = [
    ('10-moblab', ('2020-01-01 00:00:00', 'END FAIL')),
    ('12-user', ('2020-01-01 01:30:00', 'END ABORT')),
]

_TASK_RESULT_DIR = [
    ('hosts/foo/11-repair', ('2020-01-01 01:00:00', 'END GOOD')),
    ('hosts/bar/13-reset', (None, None)),  # A running job.
]


def afe_get_jobs_side_effect(id_list):
    id_ = id_list[0]
    for job, (finished_time, _) in _JOB_RESULT_DIR:
        if '{}-'.format(id_) in job:
            if not finished_time:
                return [{}]
            return [{'time_finished': finished_time}]
    return [{}]


def afe_get_task_side_effect(id_list):
    id_ = id_list[0]
    for job, (finished_time, _) in _TASK_RESULT_DIR:
        if '{}-'.format(id_) in job:
            if not finished_time:
                return [{}]
            return [{'created_on': finished_time}]
    return [{}]


class RestultUploaderTest(unittest.TestCase):
    """Unit test case for `test_result_uploader`."""
    def setUp(self):
        """Create a temp dir and some mock directories."""
        self.root_dir = pathlib.Path(tempfile.mkdtemp())
        for d, (_, status) in _JOB_RESULT_DIR + _TASK_RESULT_DIR:
            the_dir = self.root_dir / d
            the_dir.mkdir(parents=True, exist_ok=True)
            if not status:
                continue
            # Create fake status.log.
            # pylint: disable=protected-access
            with (the_dir / autotest_result._STATUS_LOG).open('w') as f:
                f.write(status)

    def tearDown(self):
        """Remove the test directory."""
        shutil.rmtree(self.root_dir, ignore_errors=True)

    @mock.patch('moblab_common.afe_connector.AFEConnector')
    def test_run_once(self, m_afe):
        args = mock.Mock(once=True)
        args.upload_timeout = datetime.timedelta(days=3)
        m_afe.get_jobs.side_effect = afe_get_jobs_side_effect
        m_afe.get_special_tasks.side_effect = afe_get_task_side_effect

        registry = [
            moblab_results_uploader.TestResultRegisteryEntry(
                root_dir=self.root_dir,
                classes=[
                    autotest_result.AutotestTestJob,
                    autotest_result.AutotestHostTask
                ]
            )
        ]
        moblab_results_uploader.run(args, test_result_registry=registry)
