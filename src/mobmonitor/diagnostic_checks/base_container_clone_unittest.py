# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for the base container clone diagnostic."""

import unittest
import mock
import sys

sys.path.append('..')
from util import osutils

import base_container_clone
import diagnostic_error

class TestBaseContainerClone(unittest.TestCase):

    def setUp(self):
        os_patch = mock.patch('base_container_clone.osutils')
        os_patch.start()
        base_container_clone.osutils.sudo_run_command.return_value = ''
        base_container_clone.osutils.RunCommandError = osutils.RunCommandError

        config_patch = mock.patch('base_container_clone.config')
        config_patch.start()
        config_mock = mock.MagicMock()
        config_mock.get.return_value = 'test'
        base_container_clone.config.Config.return_value = config_mock

    def testRun(self):
        cloner = base_container_clone.BaseContainerClone()
        expect_list = [
            'lxc-copy',
            'lxc-start',
            'lxc-stop',
            'lxc-destroy'
        ]
        result = cloner.run()
        for expect in expect_list:
            self.assertIn(expect, result)

    def testRunError(self):
        base_container_clone.osutils.sudo_run_command.side_effect = \
            osutils.RunCommandError(1, 'error')
        cloner = base_container_clone.BaseContainerClone()

        # expect first command to fail, but finally clause to execute
        expect_list = [
            'lxc-copy',
            'lxc-destroy'
        ]
        not_expect_list = [
            'lxc-start',
            'lxc-stop'
        ]

        result = cloner.run()
        for expect in expect_list:
            self.assertIn(expect, result)
        for not_expect in not_expect_list:
            self.assertNotIn(not_expect, result)


if __name__ == '__main__':
    unittest.main()
