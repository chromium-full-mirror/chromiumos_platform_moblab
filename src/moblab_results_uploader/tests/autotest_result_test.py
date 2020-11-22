# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for `autotest_result.py`."""

from __future__ import print_function

import datetime
import unittest
from unittest import mock  # pylint:disable=no-name-in-module

import autotest_result
import test_result_interface
from moblab_common import afe_connector


class AutotestHostTaskTest(unittest.TestCase):
    """Test cases for AutotestHostTask."""

    def setUp(self):
        self.task = autotest_result.AutotestHostTask(
            root_dir=".", relative_path="hosts/foo/123-task"
        )

    def test_id(self):
        """Test for getting id of Autotest host task."""
        self.assertEqual(self.task.id, "123-task")

        with self.assertRaises(test_result_interface.TestResultError):
            autotest_result.AutotestHostTask(
                root_dir=".", relative_path="hosts/foo/no_id"
            )

    def test_finished_time(self):
        """Test for getting finished time for a host task."""
        with self.assertRaises(test_result_interface.TestResultError):
            _ = self.task.finished_time

        with mock.patch.object(
            afe_connector.AFEConnector, "get_special_tasks"
        ) as m:
            m.return_value = [{"time_finished": "2020-01-01 00:00:00"}]

            task = autotest_result.AutotestHostTask(
                root_dir=".", relative_path="hosts/foo/123-task"
            )

            self.assertEqual(
                task.finished_time,
                datetime.datetime(2020, 1, 1).replace(
                    tzinfo=datetime.timezone.utc
                ),
            )

    def test_get_succeeded(self):
        """Test for getting succeeded (exit status) for a host task."""
        self.assertIsNone(self.task.succeeded)

        # Incomplete status.log.
        with mock.patch(
            "autotest_result.open", mock.mock_open(read_data="END ")
        ):
            self.assertIsNone(self.task.succeeded)

        # Exit status is FAIL
        with mock.patch(
            "autotest_result.open", mock.mock_open(read_data="BEGIN\nEND FAIL")
        ):
            self.assertFalse(self.task.succeeded)

        # Exit status is GOOD
        task = autotest_result.AutotestHostTask(
            root_dir=".", relative_path="hosts/foo/123-task"
        )
        with mock.patch(
            "autotest_result.AutotestHostTask.abs_path",
            new_callable=mock.PropertyMock,
        ) as m_abs_path:
            status_log = mock.Mock()
            m_abs_path.return_value.glob.return_value = [status_log]
            with mock.patch.object(
                status_log, "open", mock.mock_open(read_data="END GOOD YEAH!")
            ):
                self.assertTrue(task.succeeded)

    def test_job_is_not_created(self):
        """Test for ignoring ill-named result directories."""

        wrongDirectoryNames = [
            "hosts/a/123a-moblab",
            "hosts/a/a123-moblab",
            "hosts/a/123moblab",
            "hosts/123-moblab",
            "hostABC/a/123-moblab",
            "host/123-moblab",
        ]
        for relative_path in wrongDirectoryNames:
            job = autotest_result.AutotestHostTask.create(
                root_dir=".", relative_path=relative_path
            )
            self.assertIsNone(job)

    @mock.patch.object(afe_connector.AFEConnector, "get_special_tasks")
    def test_job_is_created_with_correct_job_id(self, m_get_special_tasks):
        """Test for extracting correct job id."""
        m_get_special_tasks.return_value = [
            {"time_finished": "2020-01-01 00:00:00"}
        ]

        job = autotest_result.AutotestHostTask.create(
            root_dir=".", relative_path="hosts/abc/123-moblab"
        )
        self.assertIsNotNone(job)
        self.assertEqual(job.id, "123-moblab"),

        job.finished_time
        m_get_special_tasks.assert_called_with(["123"])


class AutotestTestJobTest(unittest.TestCase):
    """Test cases for AutotestTestJob."""

    def test_id(self):
        """Test for getting id of Autotest test job."""
        r = autotest_result.AutotestTestJob(
            root_dir=".", relative_path="123-moblab"
        )
        self.assertEqual(r.id, "123-moblab")

        with self.assertRaises(test_result_interface.TestResultError):
            autotest_result.AutotestTestJob(
                root_dir=".", relative_path="no_id"
            )

    def test_finished_time_with_wrong_id(self):
        """Test for getting finished time by a non-existing job id."""
        with self.assertRaises(test_result_interface.TestResultError):
            _ = autotest_result.AutotestTestJob(
                root_dir=".", relative_path="123-moblab"
            ).finished_time

    @mock.patch.object(afe_connector.AFEConnector, "get_jobs_by_ids")
    @mock.patch.object(afe_connector.AFEConnector, "get_host_queue_entries")
    def test_job_finished_time__no_hqe(self, m_get_hqes, m_get_jobs_by_ids):
        """Test for getting finished time for a job w/o HQE."""
        m_get_jobs_by_ids.return_value = [
            {"created_on": "2020-01-01 00:00:00"}
        ]
        m_get_hqes.return_value = []

        job = autotest_result.AutotestTestJob(
            root_dir=".", relative_path="123-moblab"
        )
        self.assertEqual(job.finished_time, datetime.datetime(2020, 1, 1))

    @mock.patch.object(afe_connector.AFEConnector, "get_jobs_by_ids")
    @mock.patch.object(afe_connector.AFEConnector, "get_host_queue_entries")
    def test_job_finished_time__hqe_running(
        self, m_get_hqes, m_get_jobs_by_ids
    ):
        """Test for getting finished time for a job w/o HQE."""
        m_get_jobs_by_ids.return_value = [
            {"created_on": "2020-01-01 00:00:00"}
        ]
        m_get_hqes.return_value = [{"complete": False}]

        job = autotest_result.AutotestTestJob(
            root_dir=".", relative_path="123-moblab"
        )
        for i in range(3):
            self.assertEqual(job.finished_time, None)

    @mock.patch.object(afe_connector.AFEConnector, "get_jobs_by_ids")
    @mock.patch.object(afe_connector.AFEConnector, "get_host_queue_entries")
    def test_job_finished_time__with_hqe(self, m_get_hqes, get_jobs_by_ids):
        """Test for getting finished time for a job with HQE."""
        get_jobs_by_ids.return_value = [{"created_on": "2020-01-01 00:00:00"}]
        m_get_hqes.return_value = [
            {"finished_on": "2020-01-01 12:00:00", "complete": True},
            {"finished_on": "2020-01-01 11:00:00", "complete": True},
        ]

        job = autotest_result.AutotestTestJob(
            root_dir=".", relative_path="123-moblab"
        )
        self.assertEqual(
            job.finished_time,
            datetime.datetime(2020, 1, 1, 12).replace(
                tzinfo=datetime.timezone.utc
            ),
        )

    def test_job_is_not_created(self):
        """Test for ignoring ill-named result directories."""

        wrongDirectoryNames = ["123a-moblab", "a123-moblab", "123moblab"]
        for relative_path in wrongDirectoryNames:
            job = autotest_result.AutotestTestJob.create(
                root_dir=".", relative_path=relative_path
            )
            self.assertIsNone(job)

    @mock.patch.object(afe_connector.AFEConnector, "get_jobs_by_ids")
    @mock.patch.object(afe_connector.AFEConnector, "get_host_queue_entries")
    def test_job_is_created_with_correct_job_id(
        self, m_get_hqes, m_get_jobs_by_ids
    ):
        """Test for extracting correct job id."""
        m_get_jobs_by_ids.return_value = [
            {"created_on": "2020-01-01 00:00:00"}
        ]
        m_get_hqes.return_value = []

        job = autotest_result.AutotestTestJob.create(
            root_dir=".", relative_path="123-moblab"
        )
        self.assertIsNotNone(job)
        job.finished_time
        m_get_hqes.assert_called_with("123")


def test_get_test_result_suite_name(job_serialize_CTS):
    job = autotest_result.AutotestTestJob(
        root_dir=".", relative_path="123-moblab"
    )
    assert job.suite_name == ""

    job = autotest_result.AutotestTestJob(
        root_dir=".", relative_path="123-moblab"
    )
    with mock.patch(
        "autotest_result.AutotestTestJob.abs_path",
        new_callable=mock.PropertyMock,
    ) as m_abs_path:
        job_info = mock.Mock()
        with mock.patch.object(
            job_info, "open", mock.mock_open(read_data=job_serialize_CTS)
        ):
            m_abs_path.return_value.glob.return_value = [job_info]
            assert job.suite_name == "cts_P"
