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

import processing_step
import result_dir_status
from moblab_common import moblab_info

_LOGGER = logging.getLogger(pathlib.Path(__file__).stem)

UploadResult = collections.namedtuple('UploadResult',
                                      ['test_result', 'uploaded'])


class Uploader(processing_step.ProcessStep):
    """A class to upload a directory to GS parallelly."""
    # We use this queue to allow parallel files uploading.

    def __init__(self, *, timeout, gs_api, next_step=None):
        """Constructor

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
        self._gs_path_prefix = os.path.join(
            'results', moblab_info.get_serial_number(),
            moblab_info.get_or_create_id()
        )
        self.uploading_queue = asyncio.Queue(maxsize=10)

    async def try_upload_dir(self, test_result):
        """Try to upload a directory with timeeout checking."""
        _LOGGER.info('Try to upload dir %s', test_result)
        uploaded = False
        try:
            await self._next_step(test_result)
            await asyncio.wait_for(self.uploading_queue.join(),
                                   self._timeout.total_seconds())
            uploaded = True
        except (asyncio.TimeoutError, KeyboardInterrupt) as err:
            _LOGGER.error(
                'Error occurs when uploading %s: %s', test_result, type(err))
            if err is KeyboardInterrupt:
                raise err

        return UploadResult(test_result=test_result, uploaded=uploaded)

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


async def notify_pubsub(upload_result):
    """Notify Pubsub that the result has been uploaded."""
    if upload_result.uploaded:
        # TODO(guocb) Notify pubsub here.
        pass
    return upload_result


async def mark_uploading_result(upload_result):
    """Change test result dir status marker according to uploading result."""
    return await result_dir_status.mark_uploading_result(
        upload_result.test_result, succeeded=upload_result.uploaded)
