# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the mob-remote-scheduler"""

import unittest
from unittest import mock
from moblab_common import devserver_connector


class DevserverConnectorTest(unittest.TestCase):
    """Tests for the devserver connector."""

    def setUp(self):
        self.dev_conn = devserver_connector.DevserverConnector(
            ("test_storage_bucket")
        )

    @mock.patch("moblab_common.devserver_connector.requests.get")
    def test_devserver_command(self, mock_get_request):
        response = mock.Mock()
        response.status_code = 200
        mock_get_request.return_value = response

        result = self.dev_conn.send_devserver_command(
            "testcommand", "test_params"
        )

        self.assertTrue(result)
        mock_get_request.assert_called_once_with(
            "http://devserver:8080/testcommand?test_params", timeout=600
        )

    @mock.patch("moblab_common.devserver_connector.requests.get")
    def test_devserver_command_error(self, mock_get_request):
        response = mock.Mock()
        response.status_code = 302
        mock_get_request.return_value = response

        result = self.dev_conn.send_devserver_command(
            "testcommand", "test_params"
        )

        self.assertFalse(result)
        mock_get_request.assert_called_once_with(
            "http://devserver:8080/testcommand?test_params", timeout=600
        )

    @mock.patch("moblab_common.devserver_connector.requests.get")
    def test_devserver_command_raises(self, mock_get_request):
        test_exception = (
            devserver_connector.requests.exceptions.RequestException("Testing")
        )
        mock_get_request.side_effect = test_exception

        result = self.dev_conn.send_devserver_command(
            "testcommand", "test_params"
        )

        self.assertFalse(result)
        mock_get_request.assert_called_once_with(
            "http://devserver:8080/testcommand?test_params", timeout=600
        )

    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.send_devserver_command"
    )
    def test_stage_build_on_devserver(self, mock_send_devserver_command):

        mock_send_devserver_command.return_value = True

        result = self.dev_conn.stage_build_on_devserver(
            "gs://testarchiveurl", "t1,t2"
        )

        mock_send_devserver_command.assert_called_once_with(
            "stage", "archive_url=gs://testarchiveurl&artifacts=t1,t2"
        )
        self.assertTrue(result)

    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.send_devserver_command"
    )
    def test_check_build_staged_on_devserver(
        self, mock_send_devserver_command
    ):

        mock_send_devserver_command.return_value = True

        result = self.dev_conn.check_build_staged_on_devserver(
            "gs://testarchiveurl", "t1,t2"
        )

        mock_send_devserver_command.assert_called_once_with(
            "is_staged", "archive_url=gs://testarchiveurl&artifacts=t1,t2"
        )
        self.assertTrue(result)

    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.check_build_staged_on_devserver"
    )
    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.stage_build_on_devserver"
    )
    @mock.patch("logging.info")
    def test_stage_build(
        self,
        mock_logging,
        mock_stage_build_on_devserver,
        mock_check_build_staged_on_devserver,
    ):
        mock_check_build_staged_on_devserver.side_effect = [False, True]

        result = self.dev_conn.stage_build("testboard", "testbuild")

        self.assertTrue(result)
        mock_logging.assert_called_once()
        mock_stage_build_on_devserver.assert_called_once_with(
            "gs://test_storage_bucket/testboard-release/testbuild",
            "full_payload,autotest_packages,stateful,quick_provision",
        )

    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.check_build_staged_on_devserver"
    )
    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.stage_build_on_devserver"
    )
    @mock.patch("logging.info")
    def test_stage_build_custom_build(
        self,
        mock_logging,
        mock_stage_build_on_devserver,
        mock_check_build_staged_on_devserver,
    ):
        mock_check_build_staged_on_devserver.side_effect = [False, True]

        result = self.dev_conn.stage_build(
            "testboard", "testbuild", "testcustombuild"
        )

        self.assertTrue(result)
        mock_logging.assert_called_once()
        mock_stage_build_on_devserver.assert_called_once_with(
            "gs://test_storage_bucket/testboard-testcustombuild/testbuild",
            "full_payload,autotest_packages,stateful,quick_provision",
        )

    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.check_build_staged_on_devserver"
    )
    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.stage_build_on_devserver"
    )
    @mock.patch("logging.info")
    def test_stage_build_already_staged(
        self,
        mock_logging,
        mock_stage_build_on_devserver,
        mock_check_build_staged_on_devserver,
    ):
        mock_check_build_staged_on_devserver.return_value = True

        result = self.dev_conn.stage_build("testboard", "testbuild")

        self.assertTrue(result)
        mock_logging.assert_called_once()
        self.assertEqual(0, mock_stage_build_on_devserver.call_count)

    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.check_build_staged_on_devserver"
    )
    @mock.patch(
        "moblab_common.devserver_connector"
        ".DevserverConnector.stage_build_on_devserver"
    )
    @mock.patch("logging.info")
    def test_stage_build_failed(
        self,
        mock_logging,
        mock_stage_build_on_devserver,
        mock_check_build_staged_on_devserver,
    ):
        mock_check_build_staged_on_devserver.side_effect = [False, False]

        result = self.dev_conn.stage_build("testboard", "testbuild")

        self.assertFalse(result)
        mock_logging.assert_called_once()
        mock_stage_build_on_devserver.assert_called_once_with(
            "gs://test_storage_bucket/testboard-release/testbuild",
            "full_payload,autotest_packages,stateful,quick_provision",
        )


if __name__ == "__main__":
    unittest.main()
