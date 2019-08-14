# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the mob-remote-scheduler"""

from __future__ import print_function

import unittest
import afe_connector
import mock


class AFEConnectorTest(unittest.TestCase):
    """Testing the AfeConnector code."""

    def setUp(self):
        self.afe_conn = afe_connector.AFEConnector()

    @mock.patch('afe_connector.requests.post')
    def test_send_rpc_command(self, mock_post):
        self.afe_conn.send_rpc_command('fake_method', 'fake_params')
        mock_post.assert_called_once_with(
            'http://localhost:80/afe/server/rpc/',
            data='{"params": ["fake_params"], "id": 0, "method": "fake_method"}'
        )

    @mock.patch('afe_connector.requests.post')
    @mock.patch('chromite.lib.cros_logging.error')
    def test_send_rpc_command_fail(self, mock_logging, mock_post):
        test_exception = afe_connector.requests.exceptions.RequestException(
            'Testing')
        mock_post.side_effect = test_exception
        self.afe_conn.send_rpc_command('fake_method', 'fake_params')
        mock_post.assert_called_once_with(
            'http://localhost:80/afe/server/rpc/',
            data='{"params": ["fake_params"], "id": 0, "method": "fake_method"}'
        )
        mock_logging.assert_called_once_with(test_exception)

    def test_decode_response(self):
        response = mock.Mock()
        response.text = '{"error": null, "result": [1], "id": 0}'
        response.status_code = 200

        self.assertEqual([1], self.afe_conn.decode_response(response, 'result'))

    def test_decode_response_bad_code(self):
        response = mock.Mock()
        response.text = '{"error": null, "result": [1], "id": 0}'
        response.status_code = 302

        self.assertEqual({}, self.afe_conn.decode_response(response, 'result'))

    def test_decode_response_no_response(self):
        response = mock.Mock()
        response.text = None
        response.status_code = 302

        self.assertEqual({}, self.afe_conn.decode_response(response, 'result'))

    @mock.patch('afe_connector.AFEConnector.send_rpc_command')
    @mock.patch('afe_connector.AFEConnector.decode_response')
    def test_get_config_values(self, mock_decode_response,
                               mock_send_rpc_command):
        mock_decode_response.return_value = {
            'HOSTS': [['default_protection', 'NO_PROTECTION']],
            'AUTOTEST_WEB': [['host', 'localhost'],
                             ['database', 'chromeos_autotest_db']]
        }

        result = self.afe_conn.get_config_values()

        mock_send_rpc_command.assert_called_once()
        mock_decode_response.assert_called_once()
        self.assertDictEqual({
            'AUTOTEST_WEB': {
                'host': 'localhost', 'database': 'chromeos_autotest_db'
            }, 'HOSTS': {'default_protection': 'NO_PROTECTION'}
        }, result)

    @mock.patch('afe_connector.AFEConnector.send_rpc_command')
    @mock.patch('afe_connector.AFEConnector.decode_response')
    def test_get_connected_devices(self, mock_decode_response,
                                   mock_send_rpc_command):
        mock_decode_response.return_value = 'Testing'

        result = self.afe_conn.get_connected_devices()

        mock_send_rpc_command.assert_called_once_with('get_hosts')
        mock_decode_response.assert_called_once()
        self.assertEqual('Testing', result)

    @mock.patch('afe_connector.AFEConnector.send_rpc_command')
    def test_run_suite(self, mock_send_rpc_command):
        self.afe_conn.run_suite(
            board='test_board',
            build='test_build',
            builds='test_builds',
            suite='test_suite',
            model='test_model',
            suite_timeout_mins=5,
            suite_args='test_suite_args',
            test_args='test_test_args')
        mock_send_rpc_command.assert_called_once_with(
            'run_suite', {
                'test_args': 'test_test_args', 'suite_args': 'test_suite_args',
                'board': 'test_board', 'suite': 'test_suite',
                'model': 'test_model',
                'build': 'test_board-test_build/test_build'
            })

if __name__ == '__main__':
    unittest.main()
