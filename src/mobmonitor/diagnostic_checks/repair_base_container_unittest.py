# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for the repair base container diagnostic."""

import unittest
import mock
import sys

sys.path.append('..')
from util import osutils

import repair_base_container
import diagnostic_error

class TestRepairBaseContainer(unittest.TestCase):

    def setUp(self):
        action_patch = mock.patch('repair_base_container.moblab_actions')
        action_patch.start()

    def testRun(self):
        repair = repair_base_container.RepairBaseContainer()
        expect = 'base lxc container repaired successfully'
        self.assertEqual(expect, repair.run())

    def testRunError(self):
        repair = repair_base_container.RepairBaseContainer()
        repair.action.run.side_effect = osutils.RunCommandError(1, 'error')

        with self.assertRaises(diagnostic_error.DiagnosticError):
            repair.run()


if __name__ == '__main__':
    unittest.main()
