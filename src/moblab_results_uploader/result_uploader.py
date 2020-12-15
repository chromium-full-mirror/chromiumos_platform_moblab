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

from concurrent import futures

from moblab_common import moblab_info
from moblab_common import pubsub_client

import processing_step
import result_dir_status

_LOGGER = logging.getLogger("moblab_uploader")
_SERIAL_NUMBER = moblab_info.get_serial_number()
_MOBLAB_ID = moblab_info.get_or_create_id()
_GS_BUCKET_ROOT = "results"


class _TestResultExpiredError(Exception):
    """An error raised when a dir is expired before uploading."""


class Uploader(processing_step.ProcessStep):
    """A class to upload a directory to GS in parallel."""

    # We use this queue to allow parallel files uploading.

    def __init__(
        self, *, timeout, gs_api, next_step=None, notify_uploaded=None
    ):
        """Constructor.

        Args:
            timeout: The timeout for uploading each directory in type of
                datetime.timedelta.
            gs_api: An object of gs_api_wrapper.GsApiWrapper which wraps Google
                cloud storage API.
            next_step: A coroutine will be awaited as the next step in the
                whole pipeline.
            notify_uploaded: Callback to notify that a batch of files has been
                successfully uploaded.
        """
        super().__init__(next_step=next_step)
        self._gs_api = gs_api
        self._timeout = timeout
        self._gs_path_prefix = os.path.join(
            _GS_BUCKET_ROOT, _SERIAL_NUMBER, _MOBLAB_ID
        )
        self._uploading_context = None
        self.uploading_queue = asyncio.Queue(maxsize=0)
        self._notify_uploaded = notify_uploaded

    def uploading_context(self, ctx):
        self._uploading_context = ctx

    uploading_context = property(None, uploading_context)

    async def try_upload_dir(self, test_result):
        try:
            async with self._uploading_context(test_result) as ctx:
                try:
                    ctx.gs_path = await self._try_upload_dir(test_result)
                    if test_result.is_logged:
                        _LOGGER.debug(
                            "%s Try upload dir success %s",
                            test_result,
                            ctx.gs_path,
                        )
                except Exception:
                    ctx.gs_path = None
                    _LOGGER.exception("Try upload dir failed")
        except _TestResultExpiredError as err:
            _LOGGER.info(err)

    async def _try_upload_dir(self, test_result):
        """Try to upload a directory with timeout checking."""
        if test_result.is_logged:
            _LOGGER.info("Try to upload dir %s", test_result)
        # The GS path of uploaded test result.
        test_result_gs_path = ""
        try:
            await self._next_step(test_result)
            await asyncio.wait_for(
                self.uploading_queue.join(), self._timeout.total_seconds()
            )
            if not self._uploading_context.error:
                test_result_gs_path = os.path.join(
                    self._gs_path_prefix, test_result.name
                )
        except (asyncio.TimeoutError, KeyboardInterrupt) as err:
            _LOGGER.error(
                "Error occurs when uploading %s: %s", test_result, type(err)
            )
            if err is KeyboardInterrupt:
                raise err

        return test_result_gs_path

    async def upload_files(self, jobs=1, dry_run=False):
        """Upload files in the queue to GS in background."""
        loop = asyncio.get_event_loop()
        executor = futures.ThreadPoolExecutor(max_workers=jobs)
        awaitables = []
        result_filenames = []
        while True:
            f = await self.uploading_queue.get()
            if dry_run:
                _LOGGER.debug("DRYRUN: Uploading %s", f)
            else:
                awaitables.append(
                    loop.run_in_executor(executor, self._upload_file, f)
                )
                result_filenames.append(f)
                if self._uploading_context._test_result.is_logged:
                    _LOGGER.debug(
                        "Uploading %s, awaitables %d", f, len(awaitables)
                    )

            if self.uploading_queue.empty() or len(awaitables) >= jobs:
                if self._uploading_context._test_result.is_logged:
                    _LOGGER.debug(
                        "%s Gathering Queue len %d, awaitables %d",
                        self._uploading_context._test_result,
                        self.uploading_queue.qsize(),
                        len(awaitables),
                    )
                try:
                    results = await asyncio.gather(
                        *awaitables, return_exceptions=True
                    )
                    _LOGGER.debug(
                        "%s Gathering Results %s",
                        self._uploading_context._test_result,
                        results,
                    )
                    for result in results:
                        # If we got an error uploading a single file give up.
                        if result:
                            # One file returned error mark the upload as bad
                            self._uploading_context.error = True
                            result_filenames.clear()
                            # The only way to end the queue join is to empty
                            # the queue.
                            _LOGGER.debug(
                                "%s Error found abandoning upload. Error %s",
                                self._uploading_context._test_result,
                                result,
                            )
                            for _ in range(self.uploading_queue.qsize()):
                                # Depending on your program, you may want to
                                # catch QueueEmpty
                                try:
                                    self.uploading_queue.get_nowait()
                                    self.uploading_queue.task_done()
                                except asyncio.QueueEmpty:
                                    # This should be impossible to happen, we
                                    # have only one loop removing items from
                                    # the queue.
                                    _LOGGER.error(
                                        "Error trying to remove "
                                        "item from empty queue."
                                    )
                                    pass
                        self.uploading_queue.task_done()

                    awaitables = []
                    if self._notify_uploaded:
                        self._notify_uploaded(result_filenames)
                    result_filenames.clear()

                except Exception as e:
                    _LOGGER.debug(
                        "%s Exception thrown %s",
                        self._uploading_context._test_result,
                        str(e),
                    )

    def _upload_file(self, result_file):
        """Upload a file to GS."""
        remote_name = os.path.join(
            self._gs_path_prefix,
            result_file.test_result.name,
            result_file.relative_path,
        )
        self._gs_api.upload_from_filename(
            local_name=result_file.abs_path, remote_name=remote_name
        )


class UploadingContext(object):
    """Docstring for UploadingContext. """

    def __init__(self, *, gs_bucket, dry_run, resume_aborted=False):
        self._test_result = None
        self._gs_bucket = gs_bucket
        self.gs_path = None
        self._dry_run = dry_run
        self._resume_aborted = resume_aborted
        self.error = False

    def __call__(self, test_result):
        self._test_result = test_result
        return self

    @property
    def uploaded(self):
        return bool(self.gs_path)

    async def __aenter__(self):
        self.error = False

        if self._resume_aborted:
            return self

        if self._dry_run:
            return self

        if not await result_dir_status.mark_uploading_started(
            self._test_result
        ):
            raise _TestResultExpiredError(
                "%s is expired. Skip the uploading.", self._test_result
            )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if not self.uploaded or self.error:
            # TODO(guocb) Report failures.
            _LOGGER.debug(
                "%s Directory upload timed out, or failed uploaded=%s error=%s",
                self._test_result,
                self.uploaded,
                self.error,
            )
            return await result_dir_status.mark_uploading_result(
                self._test_result, succeeded=False
            )

        if self._dry_run:
            if self._test_result.pubsub_when_uploaded:
                _LOGGER.debug(
                    "DRYRUN: publishing message: %s",
                    os.path.join("gs://", self._gs_bucket, self.gs_path),
                )
            return

        if not self._test_result.pubsub_when_uploaded:
            if self._test_result.is_logged:
                _LOGGER.debug("%s Pubsub not requested", self._test_result)
            return await result_dir_status.mark_uploading_result(
                self._test_result, succeeded=self.uploaded
            )

        loop = asyncio.get_event_loop()
        console_client = pubsub_client.PubSubBasedClient()
        pubsub_uri = os.path.join("gs://", self._gs_bucket, self.gs_path)
        _LOGGER.debug(
            "Sending pubsub %s serialno %s moblab_id %s",
            pubsub_uri,
            _SERIAL_NUMBER,
            _MOBLAB_ID,
        )
        posted = await loop.run_in_executor(
            None,
            console_client.send_test_job_offloaded_message,
            pubsub_uri,
            _SERIAL_NUMBER,
            _MOBLAB_ID,
        )

        return await result_dir_status.mark_uploading_result(
            self._test_result, succeeded=posted
        )
