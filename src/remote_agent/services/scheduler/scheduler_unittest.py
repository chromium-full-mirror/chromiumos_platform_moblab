#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from unittest import TestCase, main
from unittest.mock import patch, PropertyMock
from concurrent.futures import Future
from io import StringIO

import scheduler

from remote_agent.constants import Constants
from remote_agent.remoteagentrpc_pb2 import MoblabHost, MoblabDut

# pylint: disable=missing-function-docstring
# pylint: disable=no-member


class SchedulerTestBase(TestCase, Constants):
    """Unit tests base class for testing the Scheduler class."""

    ATTR_TYPE = "MOBLAB_BASIC"
    DEFAULT_FREQ = 1
    WARNING_FREQ = 2
    ALERT_FREQ = 3
    NETWORK_LOW_THRES = 0
    NETWORK_MEDIUM_THRES = 1200000
    NETWORK_HIGH_THRES = 10000000
    MEMORY_LOW_THRES = 0
    MEMORY_MEDIUM_THRES = 0.5
    MEMORY_HIGH_THRES = 0.8

    def _get_mock_config(
        self,
        attr_type=ATTR_TYPE,
        default_freq=DEFAULT_FREQ,
        warning_freq=WARNING_FREQ,
        alert_freq=ALERT_FREQ,
        network_low_thres=NETWORK_LOW_THRES,
        network_medium_thres=NETWORK_MEDIUM_THRES,
        network_high_thres=NETWORK_HIGH_THRES,
        memory_low_thres=MEMORY_LOW_THRES,
        memory_medium_thres=MEMORY_MEDIUM_THRES,
        memory_high_thres=MEMORY_HIGH_THRES,
    ):
        return {
            "collectors": {
                attr_type: {
                    "frequency": {
                        "DEFAULT": default_freq,
                        "WARNING": warning_freq,
                        "ALERT": alert_freq,
                    }
                }
            },
            "network_thresholds": {
                "upload_bits_per_second": {
                    "low": network_low_thres,
                    "medium": network_medium_thres,
                    "high": network_high_thres,
                }
            },
            "memory_usage_thresholds": {
                "low": memory_low_thres,
                "medium": memory_medium_thres,
                "high": memory_high_thres,
            },
        }

    def _create_patchers(self):
        self.get_config_patcher = patch(
            "scheduler.Scheduler._get_scheduler_config"
        )
        self.collect_patcher = patch("scheduler.CollectService")
        self.upload_patcher = patch("scheduler.MessageHandler")

        self.mock_get_config = self.get_config_patcher.start()
        self.mock_collect = self.collect_patcher.start()
        self.mock_upload = self.upload_patcher.start()

    def _stop_patchers(self):
        self.get_config_patcher.stop()
        self.collect_patcher.stop()
        self.upload_patcher.stop()


class SchedulerTestCollectAndUpload(SchedulerTestBase):
    """Unit tests class for testing the Scheduler.collect_and_upload function."""

    def _set_return_values_for_mocks(
        self, moblab_return_msg=MoblabHost(), duts_return_msg=[MoblabDut()]
    ):
        self.scheduler.collect_service.collect_attr_for_moblab.return_value = (
            moblab_return_msg
        )
        self.scheduler.collect_service.collect_attr_for_duts.return_value = (
            duts_return_msg
        )
        self.scheduler.upload_service.upload_messages.return_value = ["msg_id"]

    def setUp(self):
        self._create_patchers()
        self.running_patcher = patch(
            "scheduler.Scheduler.RUNNING",
            new_callable=PropertyMock,
            side_effect=[True, False],
        )
        self.sleep_patcher = patch("scheduler.time.sleep")
        self.get_freq_level_patcher = patch(
            "scheduler.Scheduler.get_freq_level"
        )
        self.mock_running = self.running_patcher.start()
        self.mock_sleep = self.sleep_patcher.start()
        self.mock_get_freq_level = self.get_freq_level_patcher.start()

        self.scheduler = scheduler.Scheduler()

        self.scheduler.freq_level = scheduler.Frequency.DEFAULT

    def tearDown(self):
        self._stop_patchers()
        self.running_patcher.stop()
        self.sleep_patcher.stop()
        self.get_freq_level_patcher.stop()

    def test_collect_and_upload_collects_moblab_msg_type(self):
        self.scheduler.config = self._get_mock_config(
            attr_type=self.MOBLAB_BASIC
        )
        self._set_return_values_for_mocks()

        self.scheduler.collect_and_upload("moblab", self.MOBLAB_BASIC)

        self.scheduler.collect_service.collect_attr_for_moblab.assert_called_once()
        self.scheduler.collect_service.collect_attr_for_duts.assert_not_called()

    # Message types except 'moblab' and 'dut' are wrong message types.
    def test_collect_and_upload_logs_wrong_msg_type(self):
        with self.assertLogs("scheduler", level="INFO") as log:
            self.scheduler.collect_and_upload("wrong_type", self.MOBLAB_BASIC)

        self.assertIn(
            "Wrong message type, wrong_type. Message type should be 'moblab' or 'dut'.",
            log.output[0],
        )

    def test_collect_and_upload_does_not_upload_none_msg(self):
        self.scheduler.config = self._get_mock_config(
            attr_type=self.MOBLAB_BASIC
        )
        self._set_return_values_for_mocks(moblab_return_msg=None)

        with self.assertLogs("scheduler", level="INFO") as log:
            self.scheduler.collect_and_upload("moblab", self.MOBLAB_BASIC)

        self.scheduler.upload_service.upload_messages.assert_not_called()
        self.assertIn(
            "No device info is collected or uploaded.", log.output[0]
        )

    def test_collect_and_upload_runs_at_correct_interval(self):
        self.scheduler.freq_level = scheduler.Frequency.WARNING
        self.scheduler.config = self._get_mock_config(
            default_freq=1, warning_freq=3
        )
        self._set_return_values_for_mocks()

        self.scheduler.collect_and_upload("moblab", self.MOBLAB_BASIC)

        self.assertEqual(self.mock_sleep.call_count, 3)


class SchedulerTestGetFreqLevel(SchedulerTestBase):
    """Unit tests class for testing the Scheduler.get_freq_level function.

    The Scheduler.get_freq_level function is tested by initializing a Scheduler
    instance, because the initialization calls the get_freq_level function.
    """

    @patch("scheduler.open")
    @patch("scheduler.run_gcloud_bucket_diagnosis")
    @patch("scheduler.psutil.virtual_memory")
    def test_get_freq_level_succeeds_through_scheduler_initialization(
        self, mock_get_memory, mock_run_diagnosis, mock_open
    ):
        self._create_patchers()
        self.mock_collect.return_value.config_connector.get_cloud_bucket.return_value = (
            "bucket_name"
        )

        # write_throughput = 1000 * 8 = 8000 bits/sec
        network_diagnosis_res = (
            '{"write_throughput": {"bytes_per_second": 1000}, '
            + '"request_errors": 0, "connection_breaks": 0}'
        )
        network_diagnosis_file = StringIO(network_diagnosis_res)
        mock_open.return_value.__enter__.return_value = network_diagnosis_file

        # 90 percent = 0.9
        mock_get_memory.return_value.percent = 90
        self.mock_get_config.return_value = self._get_mock_config(
            network_high_thres=9000,
            network_medium_thres=5000,
            network_low_thres=0,
            memory_high_thres=0.8,
            memory_medium_thres=0.5,
            memory_low_thres=0,
        )

        test_scheduler = scheduler.Scheduler()

        # Expected freq_based_on_network_stats=WARNING, freq_based_on_memory_stats=ALERT,
        # and freq_level=ALERT.
        self.assertEqual(test_scheduler.freq_level, scheduler.Frequency.ALERT)

        self._stop_patchers()

    @patch("scheduler.Scheduler._get_freq_based_on_memory_stats")
    def test_get_freq_level_returns_freq_based_on_memory_stats_with_none_bucket(
        self, mock_get_freq_based_on_mem
    ):
        self._create_patchers()
        mock_get_freq_based_on_mem.return_value = scheduler.Frequency.WARNING
        self.mock_collect.return_value.config_connector.get_cloud_bucket.return_value = (
            None
        )

        with self.assertLogs("scheduler", level="INFO") as log:
            test_scheduler = scheduler.Scheduler()

        self.assertIn(
            "Failed to get network status: Cloud bucket name is none.",
            log.output[0],
        )
        self.assertEqual(
            test_scheduler.freq_level, scheduler.Frequency.WARNING
        )

        self._create_patchers()

    @patch("scheduler.Scheduler._get_freq_based_on_memory_stats")
    @patch("scheduler.run_gcloud_bucket_diagnosis")
    def test_get_freq_level_returns_freq_based_on_memory_stats_with_runcommanderror(
        self, mock_run_diagnosis, mock_get_freq_based_on_mem
    ):
        self._create_patchers()
        mock_get_freq_based_on_mem.return_value = scheduler.Frequency.WARNING
        self.mock_collect.return_value.config_connector.get_cloud_bucket.return_value = (
            "bucket_name"
        )
        mock_run_diagnosis.side_effect = scheduler.RunCommandError(
            1, "bad_cmd"
        )

        with self.assertLogs("scheduler", level="INFO") as log:
            test_scheduler = scheduler.Scheduler()

        self.assertIn(
            "Failed to get network status from network diagonosis: Command 'bad_cmd'"
            " returned non-zero exit status 1.",
            log.output[0],
        )
        self.assertEqual(
            test_scheduler.freq_level, scheduler.Frequency.WARNING
        )

        self._create_patchers()


class SchedulerTestSchedule(SchedulerTestBase):
    """Unit tests class for testing the Scheduler.schedule function."""

    def setUp(self):
        self._create_patchers()
        self.get_freq_level_patcher = patch(
            "scheduler.Scheduler.get_freq_level"
        )
        self.mock_get_freq_level = self.get_freq_level_patcher.start()

        self.scheduler = scheduler.Scheduler()

    def tearDown(self):
        self._stop_patchers()
        self.get_freq_level_patcher.stop()

    @patch("scheduler.ThreadPoolExecutor.submit")
    def test_schedule_creates_six_threads(self, mock_submit):
        future = Future()
        future.set_result("dummy_result")
        mock_submit.return_value = future

        self.scheduler.schedule()

        self.assertEqual(mock_submit.call_count, 6)


if __name__ == "__main__":
    main()
