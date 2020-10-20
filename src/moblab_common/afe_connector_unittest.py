# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the AFE connector"""

import http.client
import json
import sys
import time
import unittest

from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock, PropertyMock

sys.modules['docker'] = MagicMock()
sys.modules['requests'] = MagicMock()

import afe_connector


class AFEConnectorTest(unittest.TestCase):
    """Testing the AfeConnector code."""

    def setUp(self):
        self.afe_conn = afe_connector.AFEConnector()

    @mock.patch("afe_connector.requests.post")
    def test_send_rpc_command(self, mock_post):
        self.afe_conn.send_rpc_command("fake_method", "fake_params")
        mock_post.assert_called_once_with(
            "http://localhost:80/afe/server/rpc/",
            data='{"params": ["fake_params"], "id": 0, "method": "fake_method"}',
        )

    @mock.patch("afe_connector.requests.post")
    @mock.patch("chromite.lib.cros_logging.error")
    def test_send_rpc_command_fail(self, mock_logging, mock_post):
        test_exception = afe_connector.requests.exceptions.RequestException("Testing")
        mock_post.side_effect = test_exception
        self.afe_conn.send_rpc_command("fake_method", "fake_params")
        mock_post.assert_called_once_with(
            "http://localhost:80/afe/server/rpc/",
            data='{"params": ["fake_params"], "id": 0, "method": "fake_method"}',
        )
        mock_logging.assert_called_once_with(test_exception)

    def test_decode_response(self):
        response = mock.Mock()
        response.text = '{"error": null, "result": [1], "id": 0}'
        response.status_code = http.client.OK

        self.assertEqual([1], self.afe_conn.decode_response(response, "result"))

    def test_decode_response_bad_code(self):
        response = mock.Mock()
        response.text = '{"error": null, "result": [1], "id": 0}'
        response.status_code = http.client.FOUND

        self.assertEqual({}, self.afe_conn.decode_response(response, "result"))

    def test_decode_response_no_response(self):
        response = mock.Mock()
        response.text = None
        response.status_code = http.client.FOUND

        self.assertEqual({}, self.afe_conn.decode_response(response, "result"))

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    @mock.patch("afe_connector.AFEConnector.decode_response")
    def test_get_config_values(self, mock_decode_response, mock_send_rpc_command):
        mock_decode_response.return_value = {
            "HOSTS": [["default_protection", "NO_PROTECTION"]],
            "AUTOTEST_WEB": [
                ["host", "localhost"],
                ["database", "chromeos_autotest_db"],
            ],
        }

        result = self.afe_conn.get_config_values()

        mock_send_rpc_command.assert_called_once()
        mock_decode_response.assert_called_once()
        self.assertDictEqual(
            {
                "AUTOTEST_WEB": {
                    "host": "localhost",
                    "database": "chromeos_autotest_db",
                },
                "HOSTS": {"default_protection": "NO_PROTECTION"},
            },
            result,
        )

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    @mock.patch("afe_connector.AFEConnector.decode_response")
    def test_get_connected_devices(self, mock_decode_response, mock_send_rpc_command):
        mock_decode_response.return_value = "Testing"

        result = self.afe_conn.get_connected_devices()

        mock_send_rpc_command.assert_called_once_with("get_hosts")
        mock_decode_response.assert_called_once()
        self.assertEqual("Testing", result)

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_get_jobs(self, mock_send_rpc_command):
        jobs_dict = [
            {"id": 1, "name": "job1"},
            {"id": 2, "name": "job2"},
        ]
        mock_send_rpc_command.return_value = mock.MagicMock(
            status_code=http.client.OK, text=json.dumps({"result": jobs_dict})
        )

        dummy_timestamp = time.time()

        result = self.afe_conn.get_jobs(
            0,
            25,
            1,
            "job_name",
            dummy_timestamp,
            dummy_timestamp,
            sub=True,
            finished=True,
        )

        mock_send_rpc_command.assert_called_once_with(
            "get_jobs_summary",
            {
                "created_on__gt": datetime.utcfromtimestamp(
                    int(dummy_timestamp)
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "name__icontains": "job_name",
                "sub": "true",
                "query_start": 0,
                "query_limit": 25,
                "id__icontains": 1,
                "finished": "true",
                "created_on__lt": datetime.utcfromtimestamp(
                    int(dummy_timestamp)
                ).strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        self.assertEqual(jobs_dict, result)

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_get_jobs_by_ids(self, mock_send_rpc_command):
        jobs_id = [1, 2]
        jobs_dict = [
            {"id": 1, "name": "job1"},
            {"id": 2, "name": "job2"},
        ]
        mock_send_rpc_command.return_value = mock.MagicMock(
            status_code=http.client.OK, text=json.dumps({"result": jobs_dict})
        )
        result = self.afe_conn.get_jobs_by_ids(jobs_id)
        mock_send_rpc_command.assert_called_once_with(
            "get_jobs_summary", {"id__in": jobs_id}
        )
        self.assertEqual(jobs_dict, result)

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_get_special_tasks(self, mock_send_rpc_command):
        tasks_id = [1, 2]
        tasks_dict = [
            {"id": 1, "name": "task1"},
            {"id": 2, "name": "task2"},
        ]
        mock_send_rpc_command.return_value = mock.MagicMock(
            status_code=http.client.OK, text=json.dumps({"result": tasks_dict})
        )

        result = self.afe_conn.get_special_tasks(tasks_id)

        mock_send_rpc_command.assert_called_once_with(
            "get_special_tasks", {"id__in": tasks_id}
        )
        self.assertEqual(tasks_dict, result)

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_get_host_queue_entries(self, mock_send_rpc_command):
        job_id = 1
        hqes = [{"key1": "value1"}, {"key2": "value2"}]
        mock_send_rpc_command.return_value = mock.MagicMock(
            status_code=http.client.OK, text=json.dumps({"result": hqes})
        )
        result = self.afe_conn.get_host_queue_entries(job_id)

        mock_send_rpc_command.assert_called_once_with(
            "get_host_queue_entries", {"id": job_id}
        )
        self.assertEqual(hqes, result)

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_run_suite(self, mock_send_rpc_command):
        self.afe_conn.run_suite(
            board="test_board",
            build="test_build",
            builds="test_builds",
            suite="test_suite",
            model="test_model",
            suite_timeout_mins=5,
            suite_args="test_suite_args",
            test_args="test_test_args",
        )
        mock_send_rpc_command.assert_called_once_with(
            "create_suite_job",
            {
                "board": "test_board",
                "builds": "test_builds",
                "job_retry": True,
                "max_retries": 9223372036854775807,
                "max_runtime_mins": 5,
                "model": "test_model",
                "name": "test_suite",
                "pool": None,
                "run_prod_code": False,
                "suite_args": "test_suite_args",
                "test_args": "test_test_args",
                "test_source_build": "test_build",
                "timeout_mins": 5,
                "wait_for_results": True,
            },
        )

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_get_dut_wifi_info(self, mock_send_rpc_command):
        self.afe_conn.get_dut_wifi_info()
        mock_send_rpc_command.assert_called_once_with("get_dut_wifi_info", {})

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_set_configuration_info_cloud(self, mock_send_rpc_command):
        MOCK_BOTO_ACCESS_ID = 'GOOGRKMVD3VCFI51JHWM'
        MOCK_BOTO_ACCESS_KEY = 'QlZThtrb9hNfWL2R6MHbUfU7tjHUwAZPy8nyQ3c86'
        MOCK_BUCKET_NAME = 'not-a-real-moblab-bucket'

        self.afe_conn.set_configuration_info(
            gs_access_key_id=MOCK_BOTO_ACCESS_ID,
            gs_secret_access_key=MOCK_BOTO_ACCESS_KEY,
            image_storage_server=MOCK_BUCKET_NAME,
        )

        mock_send_rpc_command.assert_called_once_with(
            "submit_wizard_config_info",
            {
                'cloud_storage_info' : {
                    'gs_access_key_id' : MOCK_BOTO_ACCESS_ID,
                    'gs_secret_access_key' : MOCK_BOTO_ACCESS_KEY,
                    'image_storage_server' : MOCK_BUCKET_NAME,
                    'results_storage_server' : '',
                    'use_existing_boto_file' : False,
                    'is_cloud_enabled': True
                }
            }
        )

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_set_configuration_info_dut_wifi(self, mock_send_rpc_command):
        MOCK_DUT_WIFI_NAME = 'Fake Wifi'
        MOCK_DUT_WIFI_PASSWORD = 'perhaps934999linux'

        self.afe_conn.set_configuration_info(
            dut_wifi_name=MOCK_DUT_WIFI_NAME,
            dut_wifi_password=MOCK_DUT_WIFI_PASSWORD,
        )

        mock_send_rpc_command.assert_called_once_with(
            "submit_wizard_config_info",
            {
                'wifi_info' : {
                    'wifi_dut_ap_name' : MOCK_DUT_WIFI_NAME,
                    'wifi_dut_ap_pass' : MOCK_DUT_WIFI_PASSWORD,
                }
            }
        )

    @mock.patch("afe_connector.AFEConnector.send_rpc_command")
    def test_set_is_remote_agent_enabled(self, mock_send_rpc_command):
        MOCK_IS_ENABLED = True
        self.afe_conn.set_is_remote_agent_enabled(
            is_enabled=MOCK_IS_ENABLED
        )

        mock_send_rpc_command.assert_called_once_with(
            'set_remote_agent_config',
            {'enabled': MOCK_IS_ENABLED}
        )


if __name__ == "__main__":
    unittest.main()
