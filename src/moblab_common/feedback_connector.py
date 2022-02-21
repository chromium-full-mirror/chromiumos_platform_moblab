#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import base64
import logging
import urllib.parse

from datetime import datetime

# pylint: disable=no-name-in-module, import-error
from google.cloud import storage

from moblab_common import moblab_info
from moblab_common.utils.cli import CopyFile


class FeedbackPath:
    FEEDBACK = "feedback"
    SCREENSHOT = "screenshot"
    GCS_URL = "https://pantheon.corp.google.com/storage/browser"


class MoblabFeedbackConnector(object):
    """Class contains logic for uploading feedback information to GCS"""

    def __init__(self, moblab_bucket_name):
        self.moblab_bucket_name = moblab_bucket_name
        self.storage_client = storage.Client()

    def _get_metadata(self):
        # TODO: Feedback will eventually be extended to include additional data beyond image and feedback text.
        raise NotImplementedError

    def upload_feedback(
        self, contact_email=None, feedback=None, screenshot=None, files=[]
    ):
        """Uploads image and feedback text to GCS.

        Args:
          contact_email: string email by which feedback submitter can be contacted.
          feedback: Text string of feedback.
          screenshot: Base 64 byte string representing a png screenshot image.
          files: A list of CopyFile tuples (src, name) where src is the location of the
          file on the local machine, and name is the desired name to upload as.

        Returns:
          A tuple (path, url) where path is the directory of the uploaded info, and
          URL is a direct link to the uploaded screenshot.
        """
        bucket = self.storage_client.bucket(self.moblab_bucket_name)
        timestamp_str = str(datetime.utcnow()).split(".")[0].replace(" ", "_")
        feedback_dir_path = "/".join(
            [
                FeedbackPath.FEEDBACK,
                moblab_info.get_serial_number(),
                timestamp_str,
            ]
        )

        if screenshot:
            screenshot_blob = storage.Blob(
                feedback_dir_path + "/" + FeedbackPath.SCREENSHOT, bucket
            )
            screenshot_blob.upload_from_string(
                base64.b64decode(screenshot), content_type="image/png"
            )

        contact_and_feedback = ""
        if contact_email:
            contact_and_feedback += "Contact email: " + contact_email + "\n"
        if feedback:
            contact_and_feedback += feedback + "\n"
        if contact_and_feedback:
            feedback_blob = storage.Blob(
                feedback_dir_path + "/" + FeedbackPath.FEEDBACK, bucket
            )
            feedback_blob.upload_from_string(contact_and_feedback)

        for path, filename in files:
            filename_blob = storage.Blob(
                feedback_dir_path + "/" + filename, bucket
            )
            filename_blob.upload_from_filename(path)

        url = (
            FeedbackPath.GCS_URL
            + "/"
            + self.moblab_bucket_name
            + "/"
            + FeedbackPath.FEEDBACK
            + "/"
            + moblab_info.get_serial_number()
            + "/"
            + timestamp_str
        )

        return feedback_dir_path, url
