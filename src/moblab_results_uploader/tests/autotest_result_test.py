# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for `autotest_result.py`."""

from __future__ import print_function

import datetime
import unittest

from unittest import mock  # pylint:disable=no-name-in-module

from moblab_common import afe_connector

import autotest_result
import test_result_interface


class AutotestHostTaskTest(unittest.TestCase):
    """Test cases for AutotestHostTask."""
    def setUp(self):
        self.task = autotest_result.AutotestHostTask(
            root_dir='.', relative_path='hosts/foo/123-task')

    def test_id(self):
        """Test for getting id of Autotest host task."""
        self.assertEqual(self.task.id, '123-task')

        with self.assertRaises(test_result_interface.TestResultError):
            autotest_result.AutotestHostTask(root_dir='.',
                                             relative_path='hosts/foo/no_id')

    def test_finished_time(self):
        """Test for getting finished time for a host task."""
        with self.assertRaises(test_result_interface.TestResultError):
            _ = self.task.finished_time

        with mock.patch.object(afe_connector.AFEConnector,
                               'get_special_tasks') as m:
            m.return_value = [{'time_finished': '2020-01-01 00:00:00'}]

            task = autotest_result.AutotestHostTask(
                root_dir='.', relative_path='hosts/foo/123-task')
            self.assertEqual(task.finished_time,
                             datetime.datetime(2020, 1, 1))

    def test_get_succeeded(self):
        """Test for getting succeeded (exit status) for a host task."""
        self.assertIsNone(self.task.succeeded)

        # Incomplete status.log.
        with mock.patch('autotest_result.open',
                        mock.mock_open(read_data='END ')):
            self.assertIsNone(self.task.succeeded)

        # Exit status is FAIL
        with mock.patch('autotest_result.open',
                        mock.mock_open(read_data='BEGIN\nEND FAIL')):
            self.assertFalse(self.task.succeeded)

        # Exit status is GOOD
        with mock.patch('autotest_result.open',
                        mock.mock_open(read_data='BEGIN\nEND GOOD FOO\n')):
            task = autotest_result.AutotestHostTask(
                root_dir='.', relative_path='hosts/foo/123-task')
            self.assertTrue(task.succeeded)


class AutotestTestJobTest(unittest.TestCase):
    """Test cases for AutotestTestJob."""
    def test_id(self):
        """Test for getting id of Autotest test job."""
        r = autotest_result.AutotestTestJob(
            root_dir='.', relative_path='123-moblab')
        self.assertEqual(r.id, '123-moblab')

        with self.assertRaises(test_result_interface.TestResultError):
            autotest_result.AutotestTestJob(root_dir='.', relative_path='no_id')

    def test_finished_time_with_wrong_id(self):
        """Test for getting finished time by a non-existing job id."""
        with self.assertRaises(test_result_interface.TestResultError):
            _ = autotest_result.AutotestTestJob(
                root_dir='.', relative_path='123-moblab').finished_time

    @mock.patch.object(afe_connector.AFEConnector, 'get_jobs')
    @mock.patch.object(afe_connector.AFEConnector, 'get_host_queue_entries')
    def test_hostless_job_finished_time(self, m_get_hqes, m_get_jobs):
        """Test for getting finished time for a hostless job."""
        m_get_jobs.return_value = [{'created_on': '2020-01-01 00:00:00'}]
        m_get_hqes.return_value = []

        job = autotest_result.AutotestTestJob(
            root_dir='.', relative_path='123-moblab')
        self.assertEqual(job.finished_time,
                         datetime.datetime(2020, 1, 1))

    @mock.patch.object(afe_connector.AFEConnector, 'get_jobs')
    @mock.patch.object(afe_connector.AFEConnector, 'get_host_queue_entries')
    def test_device_job_finished_time(self, m_get_hqes, m_get_jobs):
        """Test for getting finished time for a hostless job."""
        m_get_jobs.return_value = [{'created_on': '2020-01-01 00:00:00'}]
        m_get_hqes.return_value = [
            {'finished_on': '2020-01-01 12:00:00'},
            {'finished_on': '2020-01-01 11:00:00'},
        ]

        job = autotest_result.AutotestTestJob(
            root_dir='.', relative_path='123-moblab')
        self.assertEqual(job.finished_time,
                         datetime.datetime(2020, 1, 1, 12))


def test_get_test_result_suite_name(job_serialize_CTS):
    job = autotest_result.AutotestTestJob(
        root_dir='.', relative_path='123-moblab')
    assert job.suite_name == ''

    job = autotest_result.AutotestTestJob(
        root_dir='.', relative_path='123-moblab')
    with mock.patch('autotest_result.AutotestTestJob.abs_path',
                    new_callable=mock.PropertyMock) as m_abs_path:
        job_info = mock.Mock()
        with mock.patch.object(job_info, 'open',
                               mock.mock_open(read_data=job_serialize_CTS)):
            m_abs_path.return_value.glob.return_value = [job_info]
            assert job.suite_name == 'cts_P'
