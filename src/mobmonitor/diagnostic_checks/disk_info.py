# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from moblab_common import host_connector
from util import osutils
from .diagnostic_error import DiagnosticError
from .abstract_diagnostic_check import AbstractDiagnosticCheck
import sys

sys.path.append('..')


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
        return host_connector.HostServicesConnector().get_disk_info()
