#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import base64
import datetime
import urllib

from moblab_common import moblab_info

from util import collect_logs

# pylint: disable=no-name-in-module, import-error
from google.cloud import storage

import logging

class FeedbackPath():
  FEEDBACK = 'feedback'
  SCREENSHOT= 'screenshot'
  GCS_URL = 'https://storage.cloud.google.com'


class MoblabFeedbackConnector(object):
  """Class contains logic for uploading feedback information to GCS"""
  def __init__(self, moblab_bucket_name):
    self.moblab_bucket_name = moblab_bucket_name
    self.storage_client = storage.Client()

  def _get_metadata(self):
    # TODO: Feedback will eventually be extended to include additional data beyond image and feedback text.
    raise NotImplementedError

  def upload_feedback(self, feedback=None, screenshot=None):
    """Uploads image and feedback text to GCS.

    Args:
      feedback: Text string of feedback.
      screenshot: Base 64 byte string representing a png screenshot image.

    Returns:
      A tuple (path, url) where path is the directory of the uploaded info, and
      URL is a direct link to the uploaded screenshot.
    """
    bucket = self.storage_client.bucket(self.moblab_bucket_name)
    timestamp_str = str(datetime.datetime.utcnow()).split('.')[0]
    feedback_dir_path = '/'.join([FeedbackPath.FEEDBACK, moblab_info.get_serial_number(), timestamp_str])

    if screenshot:
      screenshot_blob = storage.Blob(feedback_dir_path + '/' + FeedbackPath.SCREENSHOT, bucket)
      screenshot_blob.upload_from_string(base64.b64decode(screenshot), content_type='image/png')

    if feedback:
      feedback_blob = storage.Blob(feedback_dir_path + '/' + FeedbackPath.FEEDBACK, bucket)
      feedback_blob.upload_from_string(feedback)

    tarball = collect_logs.collect_logs()
    tarball_blob = storage.Blob(feedback_dir_path + tarball, bucket)
    tarball_blob.upload_from_filename(tarball)

    url = FeedbackPath.GCS_URL + '/' + self.moblab_bucket_name + '/' + FeedbackPath.FEEDBACK + '/' + moblab_info.get_serial_number() + '/' + urllib.parse.quote(timestamp_str) + FeedbackPath.SCREENSHOT
    return feedback_dir_path, url
