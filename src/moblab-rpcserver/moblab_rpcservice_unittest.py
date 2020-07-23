# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the MoblabService"""
import sys
import unittest

from unittest import mock
from unittest.mock import MagicMock, PropertyMock


sys.modules['moblab_common'] = MagicMock()
from moblab_rpcservice import MoblabService


class MoblabRPCServiceTest(unittest.TestCase):
  """Testing the MoblabService code."""

  def setUp(self):
    self.service = MoblabService()

  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_get_dut_wifi_info(self, mock_afe_connector):
    afe_get_dut_wifi_mock = MagicMock()
    mock_afe_connector.return_value.get_dut_wifi_info = afe_get_dut_wifi_mock

    self.service.get_dut_wifi_info()

    afe_get_dut_wifi_mock.assert_called_once()

  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_set_dut_wifi_info(self, mock_afe_connector):
    afe_set_configuration_info_mock = MagicMock()
    mock_afe_connector.return_value.set_configuration_info = afe_set_configuration_info_mock

    result_msg = self.service.set_dut_wifi_info(
        'Fake Wifi Name',
        'Fake Wifi Pass'
    )

    afe_set_configuration_info_mock.assert_called_once()
    assert isinstance(result_msg, str)

if __name__ == "__main__":
  unittest.main()
