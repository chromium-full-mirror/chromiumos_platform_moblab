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
  PauseHostSchedulerResponse,
  ResumeHostSchedulerResponse,
  GetHostSchedulerPauseStatusResponse,
  PauseRequestor,
)
from moblab_common.proto.moblab_configuration_rpc_pb2_grpc import (
    MoblabConfigurationServiceServicer,
)

from moblab_common.proto.moblab_configuration_rpc_pb2_grpc import MoblabConfigurationServiceServicer
from google.protobuf.empty_pb2 import Empty
from moblab_common.proto.moblab_settings_pb2 import MoblabSettingKey


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
        self.pause_service = HostSchedulerPauseService()

    def pause_host_scheduler(self, request, context):
        """Request pause of host scheduling"""
        requestors = self.pause_service.pause_moblab(
            self._map_to_setting(request.pauseRequestor)
        )
        return PauseHostSchedulerResponse(
            pauseRequestors=self._map_to_requestors(requestors)
        )

    def resume_host_scheduler(self, request, context):
        """Request resume of host scheduling"""
        requestors = self.pause_service.unpause_moblab(
            self._map_to_setting(request.pauseRequestor)
        )
        return ResumeHostSchedulerResponse(
            pauseRequestors=self._map_to_requestors(requestors)
        )

    def get_host_scheduler_pause_status(self, request, context):
        """Request pause of host scheduling"""
        requestors = self.pause_service.get_pause_status()
        return GetHostSchedulerPauseStatusResponse(
            pauseRequestors=self._map_to_requestors(requestors)
        )

    def _map_to_requestors(self, setting_keys):
        return [self._map_to_requestor(k) for k in setting_keys]

    def _map_to_setting(self, requestor):
        if requestor == PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE:
            return MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE

        elif requestor == PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER:
            return MoblabSettingKey.MOBLAB_SETTING_PAUSED_BY_USER

    def _map_to_requestor(self, setting_key):
        if setting_key == MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE:
            return PauseRequestor.Name(
                PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE
            )

        elif setting_key == MoblabSettingKey.MOBLAB_SETTING_PAUSED_BY_USER:
            return PauseRequestor.Name(
                PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER
            )
