# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for remote_request module."""

import sys
import unittest

import mock

import remote_request


class MoblabRemoteRequestTest(unittest.TestCase):
    """Unit tests for the MoblabRemoteRequest class."""

    def setUp(self):
        self.request = remote_request.MoblabRemoteRequest()

    @mock.patch("remote_request.uuid.uuid4")
    def test_init(self, mock_uuid):

        mock_uuid.return_value = mock.Mock()
        mock_uuid.return_value.hex = 333

        request = remote_request.MoblabRemoteRequest()

        self.assertEqual(333, request.unique_id)
        self.assertEqual(sys.maxsize, request.priority)
        self.assertEqual(sys.maxsize, request.expires_at_sec_utc)

        request = remote_request.MoblabRemoteRequest(1, 2)

        self.assertEqual(1, request.unique_id)
        self.assertEqual(2, request.priority)
        self.assertEqual(sys.maxsize, request.expires_at_sec_utc)

    def test_copy_to_proto(self):
        with self.assertRaises(NotImplementedError):
            self.request.copy_to_proto(None)

    def test_execute(self):
        with self.assertRaises(NotImplementedError):
            self.request.execute(None, None)

    def test_can_be_executed(self):
        with self.assertRaises(NotImplementedError):
            self.request.can_be_executed(None)


if __name__ == "__main__":
    unittest.main()
