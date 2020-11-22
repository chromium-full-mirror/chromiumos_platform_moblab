#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import settings_repo

from moblab_common.proto.moblab_configuration_rpc_pb2 import (
    GetSettingsRequest,
    GetSettingsResponse,
    SetSettingRequest,
    MoblabSetting,
    Value,
    MOBLAB_SETTING_LOW_DISK_SPACE,
)

from settings_repo import MoblabDb

from moblab_configuration_rpcservice import ConfigurationRpcService
from moblab_common.proto.google.protobuf.empty_pb2 import Empty

import unittest
from unittest import mock


class ConfigurationRpcServiceTest(unittest.TestCase):
    """Testing the ConfigurationRpcService code."""

    def setUp(self):
        self.rpcService = ConfigurationRpcService()

    @mock.patch.object(settings_repo.SettingsRepo, "set_setting")
    def test_set_setting(self, mock_set_setting):
        result = self.rpcService.set_setting(
            request=SetSettingRequest(
                setting=MoblabSetting(
                    key=MOBLAB_SETTING_LOW_DISK_SPACE,
                    value=Value(bool_value=False),
                )
            ),
            context={},
        )
        self.assertEqual(result, Empty())

    @mock.patch.object(settings_repo.SettingsRepo, "get_settings")
    def test_get_settings(self, mock_get_settings):
        mock_get_settings.return_value = [
            '{ "key": "MOBLAB_SETTING_LOW_DISK_SPACE", "value": { "doubleValue": 123.0 } }'
        ]
        result = self.rpcService.get_settings(
            request=GetSettingsRequest(keys=[MOBLAB_SETTING_LOW_DISK_SPACE]),
            context={},
        )
        self.assertEqual(
            result,
            GetSettingsResponse(
                moblabSettings=[
                    MoblabSetting(
                        key=MOBLAB_SETTING_LOW_DISK_SPACE,
                        value=Value(double_value=123.0),
                    )
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
