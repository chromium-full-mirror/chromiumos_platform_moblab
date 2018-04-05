# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unittests for the cloud storage speed test diagnostic."""

import unittest
import mock

import cloud_storage_speedtest
import diagnostic_error

class TestCloudStorageSpeedTest(unittest.TestCase):

    def setUp(self):
        config_patch = mock.patch('cloud_storage_speedtest.ConfigParser')
        config_patch.start()
        config_mock = mock.MagicMock()
        config_mock.sections.return_value = [1]
        config_mock.items.return_value = \
                [('image_storage_server', 'gs://bucket/')]
        cloud_storage_speedtest.ConfigParser.ConfigParser.return_value = \
                config_mock

        self.config_mock = config_mock

    def testGetBucketUrl(self):
        expect = 'gs://bucket/'
        speed_test = cloud_storage_speedtest.CloudStorageSpeedTest()
        result = speed_test._get_bucket_url()
        self.assertEqual(expect, result)

    def testMissingGetBucketUrl(self):
        self.config_mock.items.return_value = [('something', 'not bucket')]
        speed_test = cloud_storage_speedtest.CloudStorageSpeedTest()
        result = speed_test._get_bucket_url()
        self.assertEqual(None, result)

    def testProcessResults(self):
        # test 10mbps down 5mbps up
        data = """{
            "read_throughput": {
                "bytes_per_second": 1250000
            },
            "write_throughput": {
                "bytes_per_second": 625000
            }
        }"""
        expect = 'download 10.0000 mbps\nupload 5.0000 mbps'

        speed_test = cloud_storage_speedtest.CloudStorageSpeedTest()
        result = speed_test._process_results(data)
        self.assertEqual(expect, result)

if __name__ == '__main__':
    unittest.main()
