# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import ConfigParser
import json
import sys

sys.path.append('..')
from abstract_diagnostic_check import AbstractDiagnosticCheck
from diagnostic_error import DiagnosticError
from util import osutils

class DiskInfo(AbstractDiagnosticCheck):
    """
    Get information on current disk usage, mounted filesystems and their
    mount points.
    """

    category = 'System'

    name = 'Disk Info'

    description = ('Get information on current disk usage, '
    'mounted filesystems and their mount points')

    def run(self):
        try:
            result = 'df -h\n'
            cmd = ['df -h | sort -r -k 5 -i']
            result += osutils.run_command(cmd, shell=True)

            result +='\nlsblk\n'
            cmd = ['lsblk']
            result += osutils.run_command(cmd)
            return result
        except osutils.RunCommandError:
            raise DiagnosticError('Failed to gather disk information')
