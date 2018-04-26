# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for the disk info diagnostic."""

import unittest
import mock
import sys

sys.path.append('..')
from util import osutils
import disk_info
import diagnostic_error

class TestDiskInfo(unittest.TestCase):

    def setUp(self):
        os_patch = mock.patch('disk_info.osutils')
        os_patch.start()

        disk_info.osutils.run_command.return_value = 'some data'
        disk_info.osutils.RunCommandError = osutils.RunCommandError

    def testRun(self):
        expect = 'df -h\nsome data\nlsblk\nsome data'
        disk_info_test = disk_info.DiskInfo()
        result = disk_info_test.run()
        self.assertEqual(expect, result)

    def testRunError(self):
        disk_info.osutils.run_command.side_effect = \
                osutils.RunCommandError(1, 'error')
        disk_info_test = disk_info.DiskInfo()
        with self.assertRaises(diagnostic_error.DiagnosticError):
            disk_info_test.run()

if __name__ == '__main__':
    unittest.main()
