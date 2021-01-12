#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import logging
from google.protobuf import empty_pb2

from moblab_common.proto.moblab_configuration_rpc_pb2 import (
    PauseHostSchedulerResponse,
    ResumeHostSchedulerResponse,
    GetHostSchedulerPauseStatusResponse,
    PauseRequestor,
    GetStableBuildVersionResponse,
    SetStableBuildVersionResponse,
    StableVersion,
)
from moblab_common.proto.moblab_configuration_rpc_pb2_grpc import (
    MoblabConfigurationServiceServicer,
)
from host_scheduler_pause_service import HostSchedulerPauseService
from settings_store import SettingsService

from moblab_common.proto.moblab_settings_pb2 import (
    MoblabSettingKey,
    MoblabSetting,
    Value,
)


class ConfigurationRpcService(MoblabConfigurationServiceServicer):
    def __init__(self):
        super(ConfigurationRpcService, self).__init__()
        self.pause_service = HostSchedulerPauseService()
        self._settings_service = SettingsService()

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

    def get_stable_build_version(self, request, context):
        """Read stable build version configuration"""
        return GetStableBuildVersionResponse(
            stable_version=self._get_stable_build_version()
        )

    def set_stable_build_version(self, request, context):
        """Update stable build version configuration"""
        if request.stable_version.override_version is not None:
            setting = MoblabSetting(
                key=MoblabSettingKey.STABLE_CROS_VERSION_OVERRIDE,
                value=Value(
                    string_value=request.stable_version.override_version
                ),
            )
            logging.info("Setting %s", setting)
            self._settings_service.set_setting(setting=setting)

        if request.stable_version.default_version:
            setting = MoblabSetting(
                key=MoblabSettingKey.STABLE_CROS_VERSION_DEFAULT,
                value=Value(
                    string_value=request.stable_version.default_version
                ),
            )
            logging.info("Setting %s", setting)
            self._settings_service.set_setting(setting=setting)

        return SetStableBuildVersionResponse(
            stable_version=self._get_stable_build_version()
        )

    def _get_stable_build_version(self):
        keys = [
            MoblabSettingKey.STABLE_CROS_VERSION_DEFAULT,
            MoblabSettingKey.STABLE_CROS_VERSION_OVERRIDE,
        ]
        settings = self._settings_service.get_settings(keys=keys)
        default_version = next(
            (
                s
                for s in settings
                if s.key == MoblabSettingKey.STABLE_CROS_VERSION_DEFAULT
            ),
            None,
        )
        override_version = next(
            (
                s
                for s in settings
                if s.key == MoblabSettingKey.STABLE_CROS_VERSION_OVERRIDE
            ),
            None,
        )
        return StableVersion(
            default_version=default_version.value.string_value
            if default_version
            else "R86-13421.53.0",
            override_version=override_version.value.string_value
            if override_version
            else "",
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
