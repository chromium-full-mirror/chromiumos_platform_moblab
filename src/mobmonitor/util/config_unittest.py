# -*- coding: utf-8 -*-
# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest
import mock

import config


class TestConfig(unittest.TestCase):
    def setUp(self):
        config_patch = mock.patch("config.ConfigParser")
        config_patch.start()
        config_mock = mock.MagicMock()
        config_mock.sections.return_value = [1]
        config_mock.items.return_value = [
            ("testkey", "testval"),
            ("testkey2", "testval2"),
        ]
        config.ConfigParser.ConfigParser.return_value = config_mock

    def test_config_get(self):
        test_config = config.Config()
        self.assertEqual("testval", test_config.get("testkey"))
        self.assertEqual("testval2", test_config.get("testkey2"))

    def test_config_get_missing(self):
        test_config = config.Config()
        self.assertIsNone(test_config.get("testmissingkey"))


if __name__ == "__main__":
    unittest.main()
