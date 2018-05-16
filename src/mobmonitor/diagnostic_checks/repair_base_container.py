# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import sys

sys.path.append('..')
from abstract_diagnostic_check import AbstractDiagnosticCheck
from diagnostic_error import DiagnosticError
from util import osutils

from checkfiles.moblab import moblab_actions

class RepairBaseContainer(AbstractDiagnosticCheck):
    """
    Attempt to redownload the base lxc container
    """

    category = 'lxc'

    def __init__(self):
        self.action = moblab_actions.RepairBaseContainer()
        self.name = self.action.action
        self.description = self.action.info

    def run(self):
        try:
            self.action.run({})
            return 'base lxc container repaired successfully'
        except osutils.RunCommandError as e:
            raise DiagnosticError('Failed repair on ' + str(e))

