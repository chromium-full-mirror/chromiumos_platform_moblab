#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import logging

from moblab_common.proto.moblab_configuration_rpc_pb2 import (
    PauseHostSchedulerResponse,
    ResumeHostSchedulerResponse,
    GetHostSchedulerPauseStatusResponse,
)
from moblab_common.proto.moblab_configuration_rpc_pb2_grpc import (
    MoblabConfigurationServiceServicer,
)
from host_scheduler_pause_service import HostSchedulerPauseService


class ConfigurationRpcService(MoblabConfigurationServiceServicer):
    def __init__(self):
        super(ConfigurationRpcService, self).__init__()
        self.pause_service = HostSchedulerPauseService()

    def pause_host_scheduler(self, request, context):
        """Request pause of host scheduling"""
        requestors = self.pause_service.pause_moblab(request.pauseRequestor)
        return PauseHostSchedulerResponse(pauseRequestors=requestors)

    def resume_host_scheduler(self, request, context):
        """Request resume of host scheduling"""
        requestors = self.pause_service.unpause_moblab(request.pauseRequestor)
        return ResumeHostSchedulerResponse(pauseRequestors=requestors)

    def get_host_scheduler_pause_status(self, request, context):
        """Request pause of host scheduling"""
        logging.info("get_host_scheduler_pause_status is called!")
        requestors = self.pause_service.get_pause_status()
        return GetHostSchedulerPauseStatusResponse(pauseRequestors=requestors)
