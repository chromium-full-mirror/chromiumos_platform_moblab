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
from unittest.mock import patch

import settings_store
import moblab_common

from moblab_common.proto.moblab_configuration_rpc_pb2 import (
    PauseHostSchedulerRequest,
    ResumeHostSchedulerResponse,
    PauseHostSchedulerResponse,
    PauseRequestor,
)

from moblab_configuration_rpcservice import ConfigurationRpcService

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
    """Testing the ConfigurationRpcService code."""

    def setUp(self):
        self.configurationRpcService = ConfigurationRpcService()

    @patch.object(
        moblab_common.afe_connector.AFEConnector, "modify_hosts_lock_state"
    )
    @patch.object(
        moblab_common.afe_connector.AFEConnector, "get_connected_devices"
    )
    @patch.object(settings_store.SettingsStore, "get_settings")
    @patch.object(settings_store.SettingsStore, "set_setting")
    def test_pause(
        self,
        mock_set_setting,
        mock_get_settings,
        mock_get_connected_duts,
        mock_modify_hosts_lock_state,
    ):
        mock_get_settings.return_value = [
            '{ "key": "MOBLAB_SETTING_LOW_DISK_SPACE",'
            '"value": { "boolValue": false } }'
        ]
        mock_modify_hosts_lock_state.return_value = True
        mock_get_connected_duts.return_value = [
            {"hostname": "0.0.0.1"},
            {"hostname": "0.0.0.2"},
        ]

        _ = self.configurationRpcService.pause_host_scheduler(
            request=PauseHostSchedulerRequest(
                pauseRequestor=PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE
            ),
            context={},
        )
        mock_set_setting.assert_called_once_with(
            "MOBLAB_SETTING_LOW_DISK_SPACE",
            '{\n  "value": {\n    "boolValue": true\n  }\n}',
        )

    @patch.object(
        moblab_common.afe_connector.AFEConnector, "modify_hosts_lock_state"
    )
    @patch.object(
        moblab_common.afe_connector.AFEConnector, "get_connected_devices"
    )
    @patch.object(settings_store.SettingsStore, "get_settings")
    @patch.object(settings_store.SettingsStore, "set_setting")
    def test_resume(
        self,
        mock_set_setting,
        mock_get_settings,
        mock_get_connected_duts,
        mock_modify_hosts_lock_state,
    ):
        mock_get_settings.return_value = [
            '{ "key": "MOBLAB_SETTING_PAUSED_BY_USER",'
            '"value": { "boolValue": true } }'
        ]
        mock_modify_hosts_lock_state.return_value = True
        mock_get_connected_duts.return_value = [
            {"hostname": "0.0.0.1"},
            {"hostname": "0.0.0.2"},
        ]

        _ = self.configurationRpcService.resume_host_scheduler(
            request=PauseHostSchedulerRequest(
                pauseRequestor=PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER
            ),
            context={},
        )
        mock_set_setting.assert_called_once_with(
            "MOBLAB_SETTING_PAUSED_BY_USER",
            '{\n  "key": "MOBLAB_SETTING_PAUSED_BY_USER",'
            '\n  "value": {\n    "boolValue": false\n  }\n}',
        )

    # @mock.patch.object(settings_store.SettingsStore, "set_setting")
    # def test_resume(self, mock_set_setting):
    #    mock_get_settings.return_value = [
    #        '{ "key": "MOBLAB_SETTING_LOW_DISK_SPACE", "value": { "doubleValue": 123.0 } }'
    #    ]
    #    result = self.configurationRpcService.resume_host_scheduler(
    #        request=GetSettingsRequest(keys=[MOBLAB_SETTING_LOW_DISK_SPACE]),
    #        context={},
    #    )
    #    self.assertEqual(
    #        result,
    #        GetSettingsResponse(
    #            moblabSettings=[
    #                MoblabSetting(
    #                    key=MOBLAB_SETTING_LOW_DISK_SPACE,
    #                    value=Value(double_value=123.0),
    #                )
    #            ]
    #        ),
    #    )


if __name__ == "__main__":
    unittest.main()
