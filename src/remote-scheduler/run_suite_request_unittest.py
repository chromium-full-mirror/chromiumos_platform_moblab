# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for the remote requests module."""

from __future__ import print_function

import unittest
import run_suite_request


# TODO(haddowk) add more test coverage.
class MoblabSuiteRunRequestTest(unittest.TestCase):
    """Test for the runsuite request class."""

    def test_init(self):
        request = run_suite_request.MoblabSuiteRunRequest(
            1,
            'test_board',
            'test_build',
            2,
            'test_suite',
            min_duts=3,
            suite_args='suite_args',
            model='test_model',
            test_args='test_args',
            expires_at_sec_utc=3)
        self.assertEqual(1, request.unique_id)
        self.assertEqual('test_board', request.board)
        self.assertEqual('test_build', request.build)
        self.assertEqual(2, request.priority)
        self.assertEqual('test_suite', request.suite)
        self.assertEqual('test_model', request.model)
        self.assertEqual('test_args', request.test_args)
        self.assertEqual(3, request.expires_at_sec_utc)

    def test_init_with_proto(self):
        pass


if __name__ == '__main__':
    unittest.main()
