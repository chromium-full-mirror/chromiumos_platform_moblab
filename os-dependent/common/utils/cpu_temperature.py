# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import logging
import os
import threading


_LOGGER = logging.getLogger("host-server")


class CpuTemperatureException(Exception):
    """Exception class for exceptions raised by CpuTemperature"""

    pass


class CpuTemperature(object):

    # Constants for thermal zone file determination
    _THERMAL_ZONE_DIR = "/sys/class/thermal/"
    _THERMAL_ZONE_PREFIX = "thermal_zone"
    _THERMAL_ZONE_TYPE = "type"
    _THERMAL_ZONE_TEMP = "temp"
    _THERMAL_ZONE = "x86_pkg_temp"

    def __init__(self, queue_len):
        """Create instance of the CpuTemperature class

        Args:
            queue_len: Length of temperature queue (int).
        """
        self._queue_len = queue_len
        self._thermal_zone_filepath = None
        self._queue_lock = threading.Lock()
        self._temperatures = collections.deque(maxlen=self._queue_len)

    def get_temperature_queue_stats(self):
        """Returns stats about the thread safe temperatures queue.

        Returns:
            int: summation of all elements in the queue.
            int: total number of elements in the queue.
        """
        with self._queue_lock:
            return sum(self._temperatures), len(self._temperatures)

    @property
    def thermal_zone_filepath(self):
        """Determine the correct thermal_zone file to read"""
        if self._thermal_zone_filepath is None:
            thermal_zone_dirpath = None
            subdirs = [
                f for f in os.scandir(self._THERMAL_ZONE_DIR) if f.is_dir()
            ]
            for subdir in subdirs:
                if subdir.name.startswith(self._THERMAL_ZONE_PREFIX):
                    tzf = os.path.join(subdir.path, self._THERMAL_ZONE_TYPE)
                    with open(tzf, "r") as f:
                        d = f.read().strip()
                    if d == self._THERMAL_ZONE:
                        thermal_zone_dirpath = subdir.path
                        break
            else:
                # it could happen that file does not exist in the linux systems
                # So don't raise an exception at this point.
                # We are expecting to read if the file exists, and set the
                # value to zero if the file does not exist
                self._thermal_zone_filepath = "file_not_available"
                return self._thermal_zone_filepath
                
            self._thermal_zone_filepath = os.path.join(
                thermal_zone_dirpath, self._THERMAL_ZONE_TEMP
            )
        return self._thermal_zone_filepath

    def get_current_cpu_temperature(self):
        """Read thermal_zone file to get CPU temperature and update
        the thread safe temperature queue."""
        try:
            thermal_file = self.thermal_zone_filepath
            if thermal_file == "file_not_available":
                data = "0"
            else:
                with open(thermal_file, "r") as f:
                    data = f.read()
        except CpuTemperatureException:
            raise
        except Exception as e:
            raise CpuTemperatureException(
                "Unable to read %s due to: %s"
                % (self.thermal_zone_filepath, e)
            )
        with self._queue_lock:
            self._temperatures.append(float(data.strip()) / 1000)

    def flush_stale_queue(self, stale_elem_count):
        """Removes stale elements from the thread safe temperature
        queue."""
        with self._queue_lock:
            while self._temperatures and stale_elem_count > 0:
                self._temperatures.popleft()
                stale_elem_count -= 1
