# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the MoblabService"""
import sys
import unittest

from unittest import mock
from unittest.mock import MagicMock, PropertyMock


sys.modules['moblab_common'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
from feedback_connector import MoblabFeedbackConnector

MOCK_BUCKET_NAME = 'moblab-mock-bucket'
# not a real serial no
MOCK_MOBLAB_SERIAL_NO = '4HBWUSIE15646458'


class MoblabFeedbackConnectorTest(unittest.TestCase):
  """Testing the MoblabService code."""

  def setUp(self):
    self.feedback_connector = MoblabFeedbackConnector(MOCK_BUCKET_NAME)

  @mock.patch("feedback_connector.datetime")
  @mock.patch("feedback_connector.moblab_info")
  @mock.patch("feedback_connector.storage")
  def test_upload_feedback(self, mock_storage, mock_moblab_info, mock_datetime):
    mock_moblab_info.get_serial_number.return_value = MOCK_MOBLAB_SERIAL_NO
    mock_datetime.utcnow.return_value = '2020-01-01 11:11:11'

    screenshot_path, screenshot_url = self.feedback_connector.upload_feedback()
    assert(screenshot_path == 'feedback/4HBWUSIE15646458/2020-01-01 11:11:11')
    assert(screenshot_url ==
           'https://pantheon.corp.google.com/storage/browser/_details/moblab-mock-bucket/' +
           'feedback%2F4HBWUSIE15646458%2F2020-01-01%2011:11:11%2Fscreenshot')


if __name__ == "__main__":
  unittest.main()
