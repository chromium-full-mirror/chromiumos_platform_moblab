# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Repair actions for moblab health checks."""

from __future__ import print_function

import common

import os
import re

from util import osutils


class AbstractAction:

    action = 'AbstractAction'
    info = """An abstract action that needs to be implemented
    """
    param_info = {}

    def run(self, params):
        pass

#
# Disk actions.
#
class MountUsb(AbstractAction):
    action = 'Mount USB'
    info = """Mount the USB device."""
    param_info = {}

    def __init__(self, device):
        self.device = device

    def run(self, params):
        # Unmount |device| as it may already be mounted in the wrong location.
        osutils.sudo_run_command(
                ['umount', self.device], error_code_ok=True)

        # Mount |device| in the correct location.
        cmd = ['mount', self.device, common.MOBLAB_MOUNTPOINT, '-o',
                'exec,dev,nosuid']
        osutils.sudo_run_command(cmd)


class ClearOldDbRecords(AbstractAction):
    action = 'Clear Old DB Records'
    info = """Delete older database records."""
    param_info = {
        'date': ("Format 'yyyy-mm-dd'. "
                 'We keep records that are newer than the given date.')
    }

    def run(self, params):
        cmd = ['/usr/local/autotest/contrib/db_cleanup.py', params['date']]
        osutils.sudo_run_command(cmd)


class ClearLogs(AbstractAction):
    action = 'Clear Logs'
    info = """Deletes old log files."""
    param_info = {}

    def run(self, params):
        logdir = '/var/log'
        oldlog = r'^.*\.[0-9]+$'

        files_to_remove = []

        for curdir, _, files in os.walk(logdir):
          for f in files:
            if re.match(oldlog, f):
              files_to_remove.append(os.path.join(curdir, f))

        if files_to_remove:
          cmd = ['rm'] + files_to_remove
          osutils.sudo_run_command(cmd)


#
# Upstart service actions.
#
class LaunchUpstartService(AbstractAction):
    action = 'Launch Upstart Service'
    info = """Launch the upstart service."""
    param_info = {}

    def __init__(self, service):
        self.service = service

    def run(self, params):
        cmd = ['start', self.service]
        osutils.sudo_run_command(cmd)


class RepairBaseContainer(AbstractAction):
    action = 'Repair Base Container'
    info = """Redownload and reinstall the base lxc container (about 400MB)"""
    param_info = {}

    def run(self, params):
        rebuild_container = \
                ['python', '/usr/local/autotest/site_utils/lxc.py', '-s', '-f']
        osutils.sudo_run_command(rebuild_container)
        init = ['start', 'moblab-base-container-init']
        osutils.sudo_run_command(init)