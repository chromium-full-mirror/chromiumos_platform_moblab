#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import logging
import asyncio
from google.protobuf import duration_pb2, empty_pb2

from moblab_common.proto.moblab_configuration_rpc_pb2 import (
    GetLocalResultsRetentionDurationResponse,
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
from moblab_common import moblab_build_connector


class ConfigurationRpcService(MoblabConfigurationServiceServicer):
    def __init__(self):
        super(ConfigurationRpcService, self).__init__()
        self.pause_service = HostSchedulerPauseService()
        self._settings_service = SettingsService()
        self._moblab_build_connector = None

    def _init_moblab_build_connector(self):
        try:
            self._moblab_build_connector = (
                moblab_build_connector.MoblabBuildConnector()
            )
        except moblab_build_connector.MoblabBuildConnectorException:
            logging.exception("Failed to initialize MoblabBuildConnector.")
            raise

    @property
    def moblab_build_connector(self):
        if not self._moblab_build_connector:
            self._init_moblab_build_connector()

        return self._moblab_build_connector

    async def pause_host_scheduler(self, request, context):
        """Request pause of host scheduling"""
        requestors = self.pause_service.pause_moblab(
            self._map_to_setting(request.pauseRequestor)
        )
        return PauseHostSchedulerResponse(
            pauseRequestors=self._map_to_requestors(requestors)
        )

    async def resume_host_scheduler(self, request, context):
        """Request resume of host scheduling"""
        requestors = self.pause_service.unpause_moblab(
            self._map_to_setting(request.pauseRequestor)
        )
        return ResumeHostSchedulerResponse(
            pauseRequestors=self._map_to_requestors(requestors)
        )

    async def get_host_scheduler_pause_status(self, request, context):
        """Request the pause status of the host scheduler"""
        requestors = self.pause_service.get_pause_status()
        return GetHostSchedulerPauseStatusResponse(
            pauseRequestors=self._map_to_requestors(requestors)
        )

    async def stream_host_scheduler_pause_status(self, request, context):
        requestors = self.pause_service.get_pause_status()
        yield GetHostSchedulerPauseStatusResponse(
            pauseRequestors=self._map_to_requestors(requestors)
        )

        while True:
            # TODO: look into replacing polling with change event subscription
            # rpc server is the only place that changes the pause state
            await asyncio.sleep(30)
            newRequestors = self.pause_service.get_pause_status()
            if newRequestors != requestors:
                logging.info("New event in stream_host_scheduler_pause_status")
                requestors = newRequestors
                yield GetHostSchedulerPauseStatusResponse(
                    pauseRequestors=self._map_to_requestors(requestors)
                )

    async def get_stable_build_version(self, request, context):
        """Read stable build version configuration"""
        return GetStableBuildVersionResponse(
            stable_version=self._get_stable_build_version(request.board)
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

    def set_local_results_retention_duration(self, request, context):
        """Set the number of seconds the results are kept locally"""
        setting = MoblabSetting(
            key=MoblabSettingKey.LOCAL_RESULTS_RETENTION_TIME,
            value=Value(double_value=request.duration.seconds),
        )
        logging.info("Setting %s", setting)
        self._settings_service.set_setting(setting=setting)

        return empty_pb2.Empty()

    def get_local_results_retention_duration(self, request, context):
        """Get the number of seconds the results are kept locally"""
        keys = [MoblabSettingKey.LOCAL_RESULTS_RETENTION_TIME]
        settings = self._settings_service.get_settings(keys=keys)
        logging.debug("Reading %s = %s", keys, settings)
        if settings:
            return GetLocalResultsRetentionDurationResponse(
                duration=duration_pb2.Duration(
                    seconds=int(settings[0].value.double_value)
                )
            )
        # default to 3 days local results retention
        return GetLocalResultsRetentionDurationResponse(
            duration=duration_pb2.Duration(seconds=(3 * 24 * 60 * 60))
        )

    def _get_stable_build_version(self, board):
        most_stable_build = self.moblab_build_connector.get_most_stable_build(
            board
        )
        return StableVersion(
            default_version=most_stable_build,
            override_version="",
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
