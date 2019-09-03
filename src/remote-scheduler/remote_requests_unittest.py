# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for remote_requests module"""

from __future__ import print_function

import unittest

import mock

import moblab_request_pb2
import remote_request
import remote_requests
import run_suite_request


class TestRemoteRequest(remote_request.MoblabRemoteRequest):
    """Class used to test remote requests."""

    def __init__(self, unique_id=None, priority=None):
        super(TestRemoteRequest, self).__init__(unique_id, priority)

    def copy_to_proto(self, proto):
        pass

    def execute(self, devserver_connector, autotest_connector):
        pass

    def can_be_executed(self, attached_boards):
        pass

    def __str__(self):
        return 'Unique ID: %s' % self.unique_id


class MoblabRemoteRequestsTest(unittest.TestCase):
    """Unit tests for MoblabRemoteRequests."""

    def setUp(self):
        self.test_requests = remote_requests.MoblabRemoteRequests()

    def test_add_request(self):
        self.assertEqual([], self.test_requests.requests)

        request = TestRemoteRequest()
        self.test_requests.add_request(request)

        self.assertEqual(1, len(self.test_requests.requests))
        self.assertEqual(request, self.test_requests.requests[0])

    @mock.patch('chromite.lib.cros_logging.error')
    def test_load_requests_from_gcs_fails(self, mock_error_log):
        test_blob = mock.Mock()
        test_blob.path = 'test path'
        test_exception = remote_requests.exceptions.NotFound('Testing')
        test_blob.download_as_string.side_effect = test_exception

        self.test_requests.load_requests_from_gcs(test_blob)

        test_blob.download_as_string.assert_called_once()
        mock_error_log.assert_called_once_with(
            'No request list found in test path')

    @mock.patch('moblab_request_pb2.MoblabRequests')
    def test_load_requests_from_gcs(self, mock_requests_constructor):
        test_blob = mock.Mock()
        mock_requests = mock.Mock()
        mock_requests_constructor.return_value = mock_requests
        mock_requests.suite_requests = [
            moblab_request_pb2.MoblabSuiteRunRequest()
        ]
        test_blob.download_as_string.return_value = 'Test string'

        self.test_requests.load_requests_from_gcs(test_blob)

        test_blob.download_as_string.assert_called_once()
        mock_requests.ParseFromString.assert_called_once_with('Test string')
        self.assertEqual(1, len(self.test_requests.requests))

    @mock.patch('moblab_request_pb2.MoblabRequests')
    def test_save_requests_to_gcs_unknown_type(self, mock_requests_constructor):
        test_blob = mock.Mock()
        mock_requests = mock.Mock()
        mock_requests_constructor.return_value = mock_requests
        self.test_requests.add_request(TestRemoteRequest)
        with self.assertRaises(remote_requests.UnknownRequestType):
            self.test_requests.save_requests_to_gcs(test_blob)

    @mock.patch('moblab_request_pb2.MoblabRequests')
    def test_save_requests_to_gcs(self, mock_requests_constructor):
        test_blob = mock.Mock()
        mock_requests = mock.Mock()
        mock_requests_constructor.return_value = mock_requests
        mock_run_suite_request = mock.Mock(
            run_suite_request.MoblabSuiteRunRequest)
        self.test_requests.add_request(mock_run_suite_request)
        mock_proto = mock.Mock()
        mock_requests.suite_requests.add.return_value = mock_proto

        self.test_requests.save_requests_to_gcs(test_blob)

        mock_run_suite_request.copy_to_proto.assert_called_once_with(mock_proto)
        mock_requests.suite_requests.add.assert_called_once()
        mock_requests.SerializeToString.assert_called_once()

    def test_filter_requests(self):
        self.test_requests.add_request(TestRemoteRequest(1))
        self.test_requests.add_request(TestRemoteRequest(2))

        def test_filter_function(request):
            if request.unique_id == 1:
                return False
            return True

        ids = [request.unique_id for request in self.test_requests.requests]
        self.assertListEqual([1, 2], ids)

        self.test_requests.filter_requests(test_filter_function)

        ids = [request.unique_id for request in self.test_requests.requests]
        self.assertListEqual([2], ids)

    def test_sort_requests(self):
        self.test_requests.add_request(
            TestRemoteRequest(unique_id=2, priority=2))
        self.test_requests.add_request(
            TestRemoteRequest(unique_id=1, priority=1))

        ids = [request.unique_id for request in self.test_requests.requests]
        self.assertListEqual([2, 1], ids)

        self.test_requests.sort_requests()

        ids = [request.unique_id for request in self.test_requests.requests]
        self.assertListEqual([1, 2], ids)

    def test_get_request(self):
        self.test_requests.add_request(TestRemoteRequest(1))
        self.test_requests.add_request(TestRemoteRequest(2))

        self.assertEqual(1, self.test_requests.get_request().unique_id)
        self.assertEqual(2, self.test_requests.get_request(1).unique_id)
        self.assertEqual(None, self.test_requests.get_request(2))

    def test_str(self):
        self.test_requests.add_request(TestRemoteRequest(1))
        self.test_requests.add_request(TestRemoteRequest(2))

        self.assertEqual('Requests:\nUnique ID: 1\nUnique ID: 2\n',
                         str(self.test_requests))


if __name__ == '__main__':
    unittest.main()
