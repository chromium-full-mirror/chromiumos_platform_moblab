# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import copy
import logging

from utils import cpu_temperature
from utils import polling

_LOGGER = logging.getLogger("host-server")


class CpuTemperatureOrchestratorException(Exception):
    """Exception class for CpuTemperatureOrchestrator class."""

    pass


class CpuTemperatureOrchestrator(object):
    def __init__(self, period, interval):
        """Initialize CpuTemperatureOrchestrator class

        Args:
            period: Time over which the CPU temperature needs to be
                    averaged. In minutes.
            interval: Time interval for polling CPU temperatures. In
                      minutes.
        """
        self._period = period
        self._interval = interval
        # Calculate the max number of elements the temperature queue can contain
        # If period is 30 minutes, and interval is 5 minutes, then the max queue
        # length is 6.
        queue_len = self._period // self._interval
        self.cpu_temp = cpu_temperature.CpuTemperature(queue_len)
        self._poll = polling.Polling(
            self.cpu_temp.get_current_cpu_temperature, self._interval * 60
        )
        self.start_polling()

    def get_average_cpu_temperature(self):
        """Return average CPU temperature over given time."""
        try:
            if not self.is_temperature_info_valid():
                raise CpuTemperatureOrchestratorException(
                    "Temperature information is outdated"
                )
            total, length = self.cpu_temp.get_temperature_queue_stats()
            return total / length
        except ZeroDivisionError:
            _LOGGER.error("Temperature queue does not contain entries.")
        except Exception as e:
            _LOGGER.exception("Something went wrong: %s" % e)
        # After exception logging block. Restart polling if needed and
        # return None.
        self.restart_polling_if_needed()
        return None

    def is_temperature_info_valid(self):
        """Validates the temperature information."""
        mins_since_last_exec = self._poll.get_time_from_last_exec()
        # remove stale temperature values from queue. The correct
        # number of stale elements in the queue will be minutes since
        # the last successful execution divided by the interval of
        # polling (also in minutes).
        #
        # removing the stale temperature values from the queue ensures
        # that the average temperature is always calculated with
        # values obtained within the last self._period minutes.
        self.cpu_temp.flush_stale_queue(mins_since_last_exec // self._interval)
        return mins_since_last_exec < self._period

    def restart_polling_if_needed(self):
        """Restart CPU temperature polling if temperature info is
        invalid in any way."""
        # restart polling only if amount of time that has passed
        # since a successful poll is >=self._period.
        if not self.is_temperature_info_valid():
            self.stop_polling()
            self.start_polling()

    def start_polling(self):
        """Start CPU temperature polling."""
        self._poll.start()

    def stop_polling(self):
        """Stop CPU temperature polling."""
        self._poll.stop()
