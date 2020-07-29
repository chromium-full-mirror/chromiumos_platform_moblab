# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for the disk info diagnostic."""

import mock
import sys
import unittest

from unittest.mock import MagicMock

sys.path.append('..')
sys.modules['moblab_common'] = MagicMock()
import disk_info

class TestDiskInfo(unittest.TestCase):

    def setUp(self):
        pass

    def testRun(self):
        disk_info_test = disk_info.DiskInfo()
        result = disk_info_test.run()

if __name__ == '__main__':
    unittest.main()
