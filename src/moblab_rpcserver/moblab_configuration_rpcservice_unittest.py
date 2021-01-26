#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import unittest
from unittest import mock
from unittest.mock import patch

from moblab_common.database_models.moblab_settings import MoblabSettings
import settings_store
import moblab_common

from moblab_common.proto.moblab_configuration_rpc_pb2 import (
    PauseHostSchedulerRequest,
    ResumeHostSchedulerResponse,
    PauseHostSchedulerResponse,
    PauseRequestor,
)
from moblab_common.proto.moblab_settings_pb2 import MoblabSettingKey


from moblab_configuration_rpcservice import ConfigurationRpcService


class ConfigurationRpcServiceTest(unittest.IsolatedAsyncioTestCase):
    """Testing the ConfigurationRpcService code."""

    def setUp(self):
        self.configurationRpcService = ConfigurationRpcService()

    @patch.object(
        moblab_common.afe_connector.AFEConnector, "modify_hosts_lock_state"
    )
    @patch.object(
        moblab_common.afe_connector.AFEConnector, "get_connected_devices"
    )
    @patch.object(settings_store.MoblabSettingsStore, "get_settings")
    @patch.object(settings_store.MoblabSettingsStore, "set_setting")
    async def test_pause(
        self,
        mock_set_setting,
        mock_get_settings,
        mock_get_connected_duts,
        mock_modify_hosts_lock_state,
    ):
        mock_get_settings.return_value = [
            MoblabSettings(
                key=MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE,
                value='{ "key": "MOBLAB_SETTING_LOW_DISK_SPACE",'
                '"value": { "boolValue": false } }',
            )
        ]
        mock_modify_hosts_lock_state.return_value = False
        mock_get_connected_duts.return_value = [
            {"hostname": "0.0.0.1"},
            {"hostname": "0.0.0.2"},
        ]

        _ = await self.configurationRpcService.pause_host_scheduler(
            request=PauseHostSchedulerRequest(
                pauseRequestor=PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE
            ),
            context={},
        )
        mock_get_settings.assert_called()
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
    @patch.object(settings_store.MoblabSettingsStore, "get_settings")
    @patch.object(settings_store.MoblabSettingsStore, "set_setting")
    async def test_resume(
        self,
        mock_set_setting,
        mock_get_settings,
        mock_get_connected_duts,
        mock_modify_hosts_lock_state,
    ):
        mock_get_settings.return_value = [
            MoblabSettings(
                key=MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE,
                value='{ "key": "MOBLAB_SETTING_PAUSED_BY_USER",'
                '"value": { "boolValue": true } }',
            )
        ]
        mock_modify_hosts_lock_state.return_value = False
        mock_get_connected_duts.return_value = [
            {"hostname": "0.0.0.1"},
            {"hostname": "0.0.0.2"},
        ]

        _ = await self.configurationRpcService.resume_host_scheduler(
            request=PauseHostSchedulerRequest(
                pauseRequestor=PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER
            ),
            context={},
        )
        mock_get_settings.assert_called()
        mock_set_setting.assert_called_once_with(
            "MOBLAB_SETTING_PAUSED_BY_USER",
            '{\n  "key": "MOBLAB_SETTING_PAUSED_BY_USER",'
            '\n  "value": {\n    "boolValue": false\n  }\n}',
        )


if __name__ == "__main__":
    unittest.main()
