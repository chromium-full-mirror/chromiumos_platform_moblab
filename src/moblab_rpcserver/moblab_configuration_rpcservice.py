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

from moblab_common.proto.moblab_configuration_rpc_pb2 import (
  GetSettingsRequest,
  GetSettingsResponse,
  SetSettingRequest,
  MoblabSetting,
  Value,
  MOBLAB_SETTING_LOW_DISK_SPACE,
  MOBLAB_SETTING_PAUSED_BY_USER,
)

from moblab_common.proto.moblab_configuration_rpc_pb2_grpc import MoblabConfigurationServiceServicer
from google.protobuf.empty_pb2 import Empty

class ConfigurationRpcService(MoblabConfigurationServiceServicer):

    def __init__(self):
        super(ConfigurationRpcService, self).__init__()

    def get_settings(self, request, context):
        """Returns the list of requested values of Moblab settings
        """
        return GetSettingsResponse(
            moblabSettings = [
                MoblabSetting(
                    key = MOBLAB_SETTING_LOW_DISK_SPACE,
                    value = Value(bool_value = False)
                ),
                MoblabSetting(
                    key = MOBLAB_SETTING_PAUSED_BY_USER,
                    value = Value(double_value = 123)
                )]
        )

    def set_setting(self, request, context):
        """Sets the value of Moblab setting
        """
        return Empty()
