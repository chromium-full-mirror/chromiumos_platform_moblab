# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
import mock
import sys

sys.path.append('../..')

import base_container_check
from util import osutils

class TestBaseContainerCheck(unittest.TestCase):

    def setUp(self):
        config_patch = mock.patch('base_container_check.config')
        config_patch.start()
        config_mock = mock.MagicMock()
        config_mock.get.return_value = 'test_base_container'
        base_container_check.config.Config.return_value = config_mock

        osutils_patch = mock.patch('base_container_check.osutils')
        osutils_patch.start()
        base_container_check.osutils.RunCommandError = osutils.RunCommandError

    def test_check(self):
        check = base_container_check.BaseContainerCheck()
        self.assertEquals(base_container_check.BASE_CONTAINER_CODES.OK,
            check.Check())

    def test_check_missing(self):
        base_container_check.osutils.run_command.side_effect = \
            osutils.RunCommandError(1, 'error')
        check = base_container_check.BaseContainerCheck()
        self.assertEquals(
            base_container_check.BASE_CONTAINER_CODES.BASE_CONTAINER_MISSING,
            check.Check())

    def test_diagnose(self):
        check = base_container_check.BaseContainerCheck()

        diagnosis_missing = check.Diagnose(
            base_container_check.BASE_CONTAINER_CODES.BASE_CONTAINER_MISSING)
        self.assertTrue('missing' in diagnosis_missing[0])


if __name__ == '__main__':
    unittest.main()