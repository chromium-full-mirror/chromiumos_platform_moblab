# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for the remote requests module."""

from __future__ import print_function

try:
    from chromite.lib import cros_logging as logging
except ImportError:
    # pylint: disable=cros-logging-import
    import logging

# pylint: disable=no-name-in-module, import-error, wrong-import-order
from google.cloud import exceptions as cloud_exceptions

SCHEDULE_FILENAME = "scheduled_suites.data"
SCHEDULE_DIR = "scheduled_builds"


def get_executed_commands(storage_client,
                          bucket_name,
                          schedule_dir=SCHEDULE_DIR):
    """Generate a list of the request Id's that have been executed.

    The request may still be being executed, in this status executed
    means the request has been processed.

    Args:
        storage_client (object): Instantianted Google storage client object.
        bucket_name (string): The bucket to use to search for commands.
        schedule_dir (string, optional): Defaults to SCHEDULE_DIR. Path to
            search for the marker files for executed commands.

    Returns:
        list : List of strings each one being the name of a
    """
    executed = []
    blob_itr = storage_client.bucket(bucket_name).list_blobs(
        prefix=schedule_dir)
    try:
        executed = [blob.name[len(schedule_dir) + 1:] for blob in blob_itr]
    except cloud_exceptions.NotFound as e:
        logging.debug(e)
    return executed


def get_executed_contents(storage_client,
                          bucket_name,
                          unique_id,
                          schedule_dir=SCHEDULE_DIR):
    """Retrieve the debugging information placed in the lock file.

    Lock files are used to prevent commands being run multiple times, in that
    file we put some debugging information about the request, the time of
    execution and the moblab that processed it.  Retrieve that information.

    Args:
        storage_client (object): Instantianted Google storage client object.
        bucket_name (string): The bucket to use to search for commands.
        unique_id (string): The unique id of the command we want to inspect.
        schedule_dir (string, optional): Defaults to SCHEDULE_DIR. Path to
            search for the marker files for executed commands.
    """
    blob = storage_client.bucket(bucket_name).blob(
        "%s/%s" % (schedule_dir, unique_id))
    return blob.download_as_string()
