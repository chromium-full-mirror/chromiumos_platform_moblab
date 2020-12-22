# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import logging
import asyncio

from moblab_common.host_connector import HostServicesConnector
from moblab_common.host_connector import HostServicesException

from host_scheduler_pause_service import HostSchedulerPauseService
from moblab_common.proto.moblab_settings_pb2 import MoblabSettingKey


class DiskSpaceMonitorService:
    """
    Service that checks
    """

    def __init__(self):
        # TODO: threshold should be a function of the context:
        # number of DUTs, running tests suites, etc
        self._min_available_disk_space_MB = 10000
        self.pause_service = HostSchedulerPauseService()

    async def run(self):
        """Polls disk space continuously and pauses host scheduler
        if the available space amount drops below the threshold.
        The host scheduler will be unpaused when space is available again.

        The function will never return and is expect
        to be run in a background thread.
        """
        logging.info("Available disk space monitor is running.")
        while True:
            await asyncio.sleep(30)
            self._check_disk_space_threshold()

    def _check_disk_space_threshold(self):
        """Pauses host scheduler if min available space requirement
        is not met, otherwise resumes the scheduler.
        """
        disk_usage = None
        try:
            disk_usage = HostServicesConnector.get_disk_stats()
            logging.debug("Disk usage: %s", disk_usage)

        except HostServicesException:
            return False

        if disk_usage.available_MB < self._min_available_disk_space_MB:
            self.pause_service.pause_moblab(
                MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE
            )

        else:
            self.pause_service.unpause_moblab(
                MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE
            )

        return False
