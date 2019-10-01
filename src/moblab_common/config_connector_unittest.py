# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit test for the configuration connector."""

from __future__ import print_function

import unittest
import config_connector
import mock


class MoblabConfigConnector(unittest.TestCase):
    """Testing the moblab configuration connector."""

    def setUp(self):
        self.mock_afe_connector = mock.MagicMock()
        self.connector = config_connector.MoblabConfigConnector(
            self.mock_afe_connector)

    @mock.patch('config_connector.MoblabConfigConnector.load_config')
    def test_get_no_config(self, mock_load_config):
        self.connector.get('testingsection', 'testingkey')
        mock_load_config.assert_called_once()

    def test_get_success(self):
        self.mock_afe_connector.get_config_values.return_value = {
            'testingsection': {
                'testingkey': 'testingresult'
            }
        }
        value = self.connector.get('testingsection', 'testingkey')
        self.assertEqual('testingresult', value)

        # Check to ensure the caching is working
        value = self.connector.get('testingsection', 'testingkey')
        self.assertEqual('testingresult', value)
        self.mock_afe_connector.get_config_values.assert_called_once()

    def test_get_missingsection(self):
        self.mock_afe_connector.get_config_values.return_value = {
            'testingsection': {
                'testingkey': 'testingresult'
            }
        }
        value = self.connector.get('missingtestingsection', 'testingkey')
        self.assertEqual(None, value)

    def test_get_missingkey(self):
        self.mock_afe_connector.get_config_values.return_value = {
            'testingsection': {
                'testingkey': 'testingresult'
            }
        }
        value = self.connector.get('testingsection', 'missingtestingkey')
        self.assertEqual(None, value)

    def test_get_forced(self):
        self.mock_afe_connector.get_config_values.return_value = {
            'testingsection': {
                'testingkey': 'testingresult'
            }
        }
        value = self.connector.get('testingsection', 'testingkey')
        self.assertEqual('testingresult', value)

        # Check to ensure the caching is working
        value = self.connector.get(
            'testingsection', 'testingkey', force_reload=True)
        self.assertEqual('testingresult', value)
        self.assertEqual(2,
                         self.mock_afe_connector.get_config_values.call_count)


if __name__ == '__main__':
    unittest.main()
