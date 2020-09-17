# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import sys
import unittest

from unittest import mock

sys.modules['google.auth'] = mock.MagicMock()
sys.modules['google.cloud.storage'] = mock.MagicMock()
from build_connector import MoblabBuildConnector



class BuildConnectorTest(unittest.TestCase):
  """Testing the BuildConnector code."""

  BUCKET_NAME = 'partner_bucket'
  BUILD_TARGET = 'octopus'
  MODEL = 'bobba'
  MILESTONE_NO = '80'
  MILESTONE_NOS = ['79', '80']
  BUILD_VERSIONS = {
      '79' : ['1234.5.6'],
      '80' : ['1234.5.7', '1234.5.8']
  }

  # mock of the list_blobs method of google.cloud.storage.Client.Bucket objects.
  def _mock_list_blobs(self, prefix, delimiter):
    mock_blob_itr = mock.MagicMock()
    if not prefix:
      mock_blob_itr.prefixes = [
          self.BUILD_TARGET + '-release/'
      ]
    elif prefix == self.BUILD_TARGET + '-release/R':
      mock_blob_itr.prefixes = [
          self.BUILD_TARGET + '-release/R' + milestone + delimiter for milestone in \
          self.MILESTONE_NOS
      ]
    elif prefix[:len(self.BUILD_TARGET)] == self.BUILD_TARGET:
      mock_build_versions = self.BUILD_VERSIONS[
        prefix[len(self.BUILD_TARGET + '-release/R'):].strip('-')
      ]
      mock_blob_itr.prefixes = [
          prefix + build_version + delimiter for build_version in mock_build_versions]
    return mock_blob_itr

  def _create_mock_storage_client(self):
    self.gcs_client_patcher = mock.patch('build_connector.GcsClient')
    self.mock_gcs_client = self.gcs_client_patcher.start()
    mock_gcs_bucket = mock.MagicMock()
    mock_gcs_bucket.list_blobs = self._mock_list_blobs
    self.mock_gcs_client.return_value.bucket.return_value = mock_gcs_bucket

  def setUp(self):
    # mocking the google storage client
    self._create_mock_storage_client()

    self.moblab_build_connector = MoblabBuildConnector(
        self.BUCKET_NAME
    )

  def test_get_boards_available(self):
    build_targets = self.moblab_build_connector.get_boards_available()
    self.assertEqual(build_targets, [self.BUILD_TARGET])

  def test_get_milestones_available(self):
    milestones = self.moblab_build_connector.get_milestones_available(
        self.BUILD_TARGET
    )
    self.assertEqual(milestones, self.MILESTONE_NOS)

  def test_get_builds_for_milestone(self):
    build_versions = self.moblab_build_connector.get_builds_for_milestone(
        self.BUILD_TARGET, self.MILESTONE_NO)

    self.assertEqual(build_versions, self.BUILD_VERSIONS[self.MILESTONE_NO])


if __name__ == '__main__':
  unittest.main()
