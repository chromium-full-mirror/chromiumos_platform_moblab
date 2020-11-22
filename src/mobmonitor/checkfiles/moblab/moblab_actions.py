# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Repair actions for moblab health checks."""

import os
import re

from moblab_common.utils import cli


class AbstractAction:

    action = "AbstractAction"
    info = """An abstract action that needs to be implemented
    """
    param_info = {}

    def run(self, params):
        pass


#
# Disk actions.
#
class MountUsb(AbstractAction):
    action = "Mount USB"
    info = """Mount the USB device."""
    param_info = {}

    def __init__(self, device):
        self.device = device

    def run(self, params):
        pass


class ClearOldDbRecords(AbstractAction):
    action = "Clear Old DB Records"
    info = """Delete older database records."""
    param_info = {
        "date": (
            "Format 'yyyy-mm-dd'. "
            "We keep records that are newer than the given date."
        )
    }

    def run(self, params):
        cmd = ["/usr/local/autotest/contrib/db_cleanup.py", params["date"]]
        cli.sudo_run_command(cmd)


class ClearLogs(AbstractAction):
    action = "Clear Logs"
    info = """Deletes old log files."""
    param_info = {}

    def run(self, params):
        logdir = "/var/log"
        oldlog = r"^.*\.[0-9]+$"

        files_to_remove = []

        for curdir, _, files in os.walk(logdir):
            for f in files:
                if re.match(oldlog, f):
                    files_to_remove.append(os.path.join(curdir, f))

        if files_to_remove:
            cmd = ["rm"] + files_to_remove
            cli.sudo_run_command(cmd)


#
# Upstart service actions.
#
class LaunchUpstartService(AbstractAction):
    action = "Launch Upstart Service"
    info = """Launch the upstart service."""
    param_info = {}

    def __init__(self, service):
        self.service = service

    def run(self, params):
        cmd = ["start", self.service]
        cli.sudo_run_command(cmd)
