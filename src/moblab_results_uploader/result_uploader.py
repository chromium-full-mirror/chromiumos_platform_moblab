# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This module defines classes and/or other utils for uploading to GS."""
from __future__ import print_function

import asyncio
import collections
import logging  # pylint: disable=cros-logging-import
import os
import pathlib

from moblab_common import moblab_info
from moblab_common import pubsub_client

import processing_step
import result_dir_status

_LOGGER = logging.getLogger(pathlib.Path(__file__).stem)
_SERIAL_NUMBER = moblab_info.get_serial_number()
_MOBLAB_ID = moblab_info.get_or_create_id()
_GS_BUCKET_ROOT = 'results'


class UploadResult(collections.namedtuple(
    'UploadResult', ['test_result', 'test_result_gs_path'])):
    @property
    def uploaded(self):
        return self.test_result_gs_path != ''


class Uploader(processing_step.ProcessStep):
    """A class to upload a directory to GS in parallel."""
    # We use this queue to allow parallel files uploading.

    def __init__(self, *, timeout, gs_api, next_step=None):
        """Constructor.

        Args:
            timeout: The timeout for uploading each directory in type of
                datetime.timedelta.
            gs_api: An object of gs_api_wrapper.GsApiWrapper which wraps Google
                cloud storage API.
            next_step: A coroutine will be awaited as the next step in the
                whole pipeline.
        """
        super().__init__(next_step=next_step)
        self._gs_api = gs_api
        self._timeout = timeout
        self._gs_path_prefix = os.path.join(_GS_BUCKET_ROOT, _SERIAL_NUMBER,
                                            _MOBLAB_ID)
        self.uploading_queue = asyncio.Queue(maxsize=10)

    async def try_upload_dir(self, test_result):
        """Try to upload a directory with timeout checking."""
        _LOGGER.info('Try to upload dir %s', test_result)
        # The GS path of uploaded test result.
        test_result_gs_path = ''
        try:
            await self._next_step(test_result)
            await asyncio.wait_for(self.uploading_queue.join(),
                                   self._timeout.total_seconds())
            test_result_gs_path = os.path.join(self._gs_path_prefix,
                                               test_result.name)
        except (asyncio.TimeoutError, KeyboardInterrupt) as err:
            _LOGGER.error(
                'Error occurs when uploading %s: %s', test_result, type(err))
            if err is KeyboardInterrupt:
                raise err

        return UploadResult(test_result=test_result,
                            test_result_gs_path=test_result_gs_path)

    async def upload_files(self):
        """Upload files in the queue to GS in background."""
        loop = asyncio.get_event_loop()
        while True:
            f = await self.uploading_queue.get()
            _LOGGER.debug('Uploading %s', f)
            await loop.run_in_executor(None, self._upload_file, f)
            _LOGGER.debug('Done: %s', f)
            self.uploading_queue.task_done()

    def _upload_file(self, result_file):
        """Upload a file to GS."""
        remote_name = os.path.join(self._gs_path_prefix,
                                   result_file.test_result.name,
                                   result_file.relative_path)
        self._gs_api.upload_from_filename(local_name=result_file.abs_path,
                                          remote_name=remote_name)


class PostUploading(object):
    """Processing after uploading, e.g. pubsub, report failures, etc."""

    def __init__(self, gs_bucket):
        self._gs_bucket = gs_bucket

    async def process(self, upload_result):
        """Process the upload result and run post actions accordingly.

        When uploading failed, we record the failure in a report.

        When uploading succeeded, we send a pubsub event. We then update the
        status file according to the event sending result.

        For some test result, e.g. AutotestHostTask, we don't want to send
        pubsub event in this case, so just update status file directly
        according to the uploading result.
        """
        test_result = upload_result.test_result
        if not upload_result.uploaded:
            # TODO(guocb) Report failures.
            return

        if not test_result.pubsub_when_uploaded:
            return await result_dir_status.mark_uploading_result(
                test_result, succeeded=upload_result.uploaded)

        loop = asyncio.get_event_loop()
        console_client = pubsub_client.PubSubBasedClient()
        posted = await loop.run_in_executor(
            None, console_client.send_test_job_offloaded_message,
            os.path.join('gs://', self._gs_bucket,
                         upload_result.test_result_gs_path),
            _SERIAL_NUMBER, _MOBLAB_ID)

        return await result_dir_status.mark_uploading_result(
            test_result, succeeded=posted)
