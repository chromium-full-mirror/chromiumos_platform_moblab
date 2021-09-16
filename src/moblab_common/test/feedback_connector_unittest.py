# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the MoblabService"""
import sys
import unittest

from unittest import mock
from unittest.mock import MagicMock

from moblab_common import feedback_connector

# sys.modules["moblab_common"] = MagicMock()
# sys.modules["google.cloud"] = MagicMock()

MOCK_BUCKET_NAME = "moblab-mock-bucket"
# not a real serial no
MOCK_MOBLAB_SERIAL_NO = "4HBWUSIE15646458"


class MoblabFeedbackConnectorTest(unittest.TestCase):
    """Testing the MoblabService code."""

    @mock.patch("google.cloud.storage.Client")
    @mock.patch("moblab_common.feedback_connector.datetime")
    @mock.patch("moblab_common.feedback_connector.moblab_info")
    @mock.patch("moblab_common.feedback_connector.storage")
    def test_upload_feedback(
        self, mock_storage, mock_moblab_info, mock_datetime, mock_google_client
    ):
        mock_moblab_info.get_serial_number.return_value = MOCK_MOBLAB_SERIAL_NO
        mock_datetime.utcnow.return_value = "2020-01-01 11:11:11"

        self.fd_connector = feedback_connector.MoblabFeedbackConnector(
            MOCK_BUCKET_NAME
        )
        r = self.fd_connector.upload_feedback(
            contact_email="fake@email.com",
            feedback="Feedback feedback feedback.",
            files=[("/mock/path/to/tar", "files.tgz")],
        )
        self.assertEqual(r[0], "feedback/4HBWUSIE15646458/2020-01-01_11:11:11")
        self.assertEqual(
            r[1],
            "https://pantheon.corp.google.com/storage/browser/_details/"
            "moblab-mock-bucket/feedback/4HBWUSIE15646458/2020-01-01_11:11:11/"
            "screenshot",
        )


if __name__ == "__main__":
    unittest.main()
