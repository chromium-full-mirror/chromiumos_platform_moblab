# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This module defines some coroutines to check test result status."""
from __future__ import print_function

import collections
import datetime
import enum
import logging

import processing_step
import test_result_interface
from moblab_common import lock_util

MARKER_FILE = ".uploader_status"
_MARKER_LOCK_FILE = ".uploader_status.lock"

_LOGGER = logging.getLogger("moblab_uploader")


Status = enum.Enum(
    "Status", ["NOT_READY", "READY", "UPLOADING", "UPLOADED", "EXPIRED"]
)
ResultAndStatus = collections.namedtuple(
    "ResultAndStatus", ["status", "test_result"]
)


async def _load_status(test_result):
    """Load status of the `test_result` from status file."""
    try:
        status_str = (test_result.abs_path / MARKER_FILE).read_text()
    except FileNotFoundError:
        return Status.NOT_READY
    for status in Status:
        if status.name == status_str:
            return status

    return Status.NOT_READY


async def _write_status(test_result, status):
    """Write new `status` to status file of the `test_result_state`."""
    if test_result.is_logged:
        _LOGGER.info("change status of %s to %s", test_result, status)
    (test_result.abs_path / MARKER_FILE).write_text(status.name)


async def mark_uploading_started(test_result):
    """Change the test result status to UPLOADING."""
    with lock_util.file_lock(
        test_result.abs_path / _MARKER_LOCK_FILE, exclusive=True
    ):
        previous_status = await _load_status(test_result)
        # Should have been expired, so skip the uploading.
        if previous_status != Status.READY:
            return False

        await _write_status(test_result, Status.UPLOADING)
        return True


async def mark_uploading_result(test_result, *, succeeded):
    """Change the test result status according to uploading result."""
    with lock_util.file_lock(
        test_result.abs_path / _MARKER_LOCK_FILE, exclusive=True
    ):
        await _write_status(
            test_result, Status.UPLOADED if succeeded else Status.NOT_READY
        )


class ResultStatusChecker(processing_step.ProcessStep):
    """A class to check current test result status for uploading."""

    def __init__(self, *, min_age_to_upload, min_age_to_prune, next_step=None):
        self._min_age_to_upload = min_age_to_upload
        self._min_age_to_prune = min_age_to_prune
        self._next_step = next_step

    def _check_latest_status(self, test_result, previous_status):
        # check test_result finished time to determine the status.
        try:
            finished_time = test_result.finished_time
        except test_result_interface.TestResultError as ex:
            _LOGGER.warning(
                "Cannot get info of %s from scheduler, keep retrying. "
                "Exception: %s",
                test_result,
                ex,
            )
            # TODO(haddowk) Figure out a way to expire these jobs after
            # a certain amount of time.
            return Status.NOT_READY

        if not finished_time:
            return Status.NOT_READY

        age = datetime.timedelta()
        try:
            age = datetime.datetime.now(datetime.timezone.utc) - finished_time
        except TypeError:
            _LOGGER.error("Unable to determine age - default to 0")
            _LOGGER.error(finished_time)

        if previous_status not in [Status.UPLOADED]:
            if test_result.is_logged:
                _LOGGER.debug(
                    "%s finished on %s age %s", test_result, finished_time, age
                )

        if age < self._min_age_to_upload:
            return Status.NOT_READY

        if age > self._min_age_to_prune and previous_status in [
            Status.UPLOADED
        ]:
            if test_result.is_logged:
                _LOGGER.debug(
                    "%s Job is past the max age - expire", test_result
                )
            return Status.EXPIRED

        if previous_status == Status.NOT_READY:
            if test_result.is_logged:
                _LOGGER.debug(
                    "%s Not running and in the age range to upload.",
                    test_result,
                )
            return Status.READY

        return previous_status

    async def check(self, test_result):
        """Check current status and upload the test result if OK.

        We use MARKER_FILE to save result directory status:
        - EXPIRED: which means it should be pruned, but not
        complete yet.
        - UPLOADING: which means a thread is uploading it. We don't prune
        directory in this state even though it's expired.
        - Other status (i.e. NOT_READY, UPLOADED), we will check the latest
        time according to the finished time to see if it is ready for UPLOADING
        or has EXPIRED.
        """
        try:
            with lock_util.file_lock(
                test_result.abs_path / _MARKER_LOCK_FILE, exclusive=True
            ):
                previous_status = await _load_status(test_result)
                if test_result.is_logged and previous_status not in [
                    Status.UPLOADED
                ]:
                    _LOGGER.debug(
                        "%s Previous status %s", test_result, previous_status
                    )
                current_status = previous_status
                if previous_status not in [Status.EXPIRED, Status.UPLOADING]:
                    current_status = self._check_latest_status(
                        test_result, previous_status
                    )
                if test_result.is_logged and previous_status != current_status:
                    _LOGGER.debug(
                        "%s Current status %s", test_result, current_status
                    )
                if previous_status != current_status:
                    await _write_status(test_result, current_status)
        except FileNotFoundError:
            _LOGGER.exception(
                "The directory may be pruned just before checking."
            )
            return

        if current_status in [Status.EXPIRED, Status.READY, Status.UPLOADING]:
            await self._next_step(
                ResultAndStatus(status=current_status, test_result=test_result)
            )

    async def get_last_status(self, test_result):
        """Run next step with 'last' (may out of date) directory status."""
        last_status = await _load_status(test_result)
        await self._next_step(
            ResultAndStatus(status=last_status, test_result=test_result)
        )


class StatusFilter(processing_step.ProcessStep):
    def __init__(self, *status, next_step=None):
        super().__init__(next_step=next_step)
        self._status = status

    async def filter(self, result_and_status):
        if result_and_status.status in self._status:
            await self._next_step(result_and_status.test_result)
