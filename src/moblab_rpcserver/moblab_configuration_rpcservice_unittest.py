#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import calendar
import datetime
import grpc
import logging
import re
import time

import moblab_service

from moblab_configuration_rpc_pb2 import (
  GetSettingsRequest,
  GetSettingsResponse,
  SetSettingRequest,
  MoblabSetting,
  Value,
  MOBLAB_SETTING_LOW_DISK_SPACE,
)

from moblab_configuration_rpcservice import ConfigurationRpcService
from google.protobuf.empty_pb2 import Empty

import unittest

from unittest import mock
from unittest.mock import MagicMock, PropertyMock

class ConfigurationRpcServiceTest(unittest.TestCase):
  """Testing the ConfigurationRpcService code."""

  def setUp(self):
    self.rpcService = ConfigurationRpcService()

  def test_set_setting(self):
    result = self.rpcService.set_setting(
        request = SetSettingRequest(
            setting = MoblabSetting(
                key = MOBLAB_SETTING_LOW_DISK_SPACE,
                value = Value(bool_value = False)
            )
        ),
        context = {}
    )
    self.assertEqual(result, Empty())

  def test_get_settings(self):
    result = self.rpcService.get_settings(
        request = GetSettingsRequest(
            keys = [MOBLAB_SETTING_LOW_DISK_SPACE]
        ),
        context = {}
    )
    self.assertEqual(result, GetSettingsResponse())

if __name__ == '__main__':
    unittest.main()
