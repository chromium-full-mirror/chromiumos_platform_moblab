# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import datetime
import logging
import threading
import time

_LOGGER = logging.getLogger("host-server")


class Polling(object):
    def __init__(self, target_funct, interval):
        """Instantiate Polling class.

        Args:
            target_funct: Function that needs to be polled.
            interval: Interval (in seconds) between each polling call.
        """
        self._poll_interval = interval
        self._target_funct = target_funct
        # Set thread's initial running state.
        self._running = False
        self._last_execution_timestamp = None

    def get_time_from_last_exec(self):
        """Returns minutes elapsed since the last successful execution
        of self._target_funct"""
        if not self._last_execution_timestamp:
            # Execution has never been successful.
            return int("inf")
        curr_time = datetime.datetime.now()
        time_delta = curr_time - self._last_execution_timestamp
        return time_delta.total_seconds() // 60

    def start(self):
        """Starts the thread."""
        self._running = True
        self._thread = threading.Thread(target=self.poll)
        self._thread.daemon = True
        self._thread.start()

    def poll(self):
        """Polls the target function."""
        while self._running:
            try:
                self._target_funct()
            except Exception as e:
                _LOGGER.exception(
                    "An exception occured while executing %s: %s"
                    % (self._target_funct.__name__, e)
                )
                self.error = str(e)
            else:
                # Target function executed successfully.
                self._last_execution_timestamp = datetime.datetime.now()
            time.sleep(self._poll_interval)

    def stop(self):
        """Gracefully stop thread.

        Blocking function exits only when self.is_alive() returns a
        False. See self.is_alive() method for more details on how long
        it may take to finish.
        """
        self._running = False
        while self.is_alive():
            pass

    def is_alive(self):
        """Check if thread is alive.

        This method will return true even if self._running is set to
        False. self._running is an indicator of what state the thread
        should be in - running or stopped, and does not indicate the
        alive-ness of the thread.
        """
        # self._thread.is_alive() could remain alive for a mximum of
        # time set in self._poll_interval
        return self._thread and self._thread.is_alive()
