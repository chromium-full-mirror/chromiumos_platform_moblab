#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import settings_store

from moblab_common.proto.moblab_configuration_rpc_pb2 import (
    PauseHostSchedulerRequest,
    ResumeHostSchedulerResponse,
    PauseHostSchedulerResponse,
    PauseRequestor,
)

from moblab_common.database_models.moblab_settings import MoblabSettings

from moblab_configuration_rpcservice import ConfigurationRpcService
from google.protobuf.empty_pb2 import Empty


import unittest
from unittest import mock


class ConfigurationRpcServiceTest(unittest.TestCase):
    """Testing the ConfigurationRpcService code."""

    def setUp(self):
        self.configurationRpcService = ConfigurationRpcService()

    @mock.patch.object(settings_store.SettingsStore, "set_setting")
    @mock.patch.object(settings_store.SettingsStore, "get_settings")
    def test_pause(self, mock_get_settings, mock_set_setting):
        mock_get_settings.return_value = [
            '{ "key": "MOBLAB_SETTING_LOW_DISK_SPACE", "value": { "boolValue": true } }'
        ]
        response = self.configurationRpcService.pause_host_scheduler(
            request=PauseHostSchedulerRequest(
                pauseRequestor=PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE
            ),
            context={},
        )
        expectedResponse = PauseHostSchedulerResponse(
            pauseRequestors=[PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE],
        )
        self.assertEqual(response, expectedResponse)


if __name__ == "__main__":
    unittest.main()
