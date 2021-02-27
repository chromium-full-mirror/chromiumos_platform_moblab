# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# TODO(guocb) Move this wrapper to moblab_common and integreated with
# moblab_common/versioned_upload.py

"""A wrapper of Google Cloud Storage API."""

import asyncio
import gzip
import logging  # pylint: disable=cros-logging-import
import os
import random
import requests
import shutil
import tempfile
import time
import urllib3

from google.cloud import exceptions as gcp_exceptions
from google.cloud import storage as gs

from retry.api import retry_call

ENV_GOOGLE_APP_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"
_LOGGER = logging.getLogger("moblab_uploader")

"""
    Defines what GsApiWrapper will compress before uploading, and what it will not
    compress before uploading.

    Args:
        path: a pathlib.Path object representing the file targeted for upload.

    Returns:
        Boolean that is true if the file will not be gzipped before upload
"""
def do_not_gzip(path):
    return path.suffix.endswith("gz") or path.suffix.endswith("zip")


class GsAccessError(Exception):
    """Exceptions raised when access the GS bucket."""


def _get_gs_bucket(gs_bucket, credentials_file):
    """Get GS bucket object with permission checking.

    Args:
          gs_bucket: The Google Storage bucket name, without 'gs://' prefix.
          credentials_file: The path of the credentials file.

    Returns:
        A google.cloud.bucket object.

    Raises:
        GsAccessError when we can't access the bucket or don't have enough
        permission.
    """
    _LOGGER.info("Verify the access to Google Storage.")
    if not credentials_file:
        raise GsAccessError("No credential file specified.")
    os.environ[ENV_GOOGLE_APP_CREDENTIALS] = credentials_file
    client = gs.Client()

    try:
        bucket = client.get_bucket(gs_bucket)
    except (gcp_exceptions.Forbidden, gcp_exceptions.NotFound) as err:
        raise GsAccessError(str(err))

    # Test the write permission.
    if bucket.test_iam_permissions(["storage.objects.create"]):
        return bucket

    raise GsAccessError(
        "You don't have write permission to the bucket:{}".format(gs_bucket)
    )


class GsApiWrapper(object):
    """A wrapper of Google Cloud Storage API."""

    def __init__(self, gs_bucket, credentials_file):
        """Constructor.

        Args:
            gs_bucket: The Google Storage bucket name, without 'gs://' prefix.
            credentials_file: The path of the credentials file.
        """
        self._bucket_name = gs_bucket
        self._credentials_file = credentials_file
        self._gs_bucket = _get_gs_bucket(
            self._bucket_name, self._credentials_file
        )
        self._client = gs.Client()

    def _gzip_file(self, local_name):
        zipped_file = tempfile.mktemp()
        with open(local_name, "rb") as f_in:
            with gzip.open(zipped_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        return zipped_file

    """
        Uploads 'local_name' file to the GCS bucket that GsApiWrapper has been
        initialized to.

        Args:
            local_name: a pathlib.Path object representing the file targeted for upload.
            remote_name: a string representing the intended name of the file once
            uploaded.
    """
    def upload_from_filename(self, *, local_name, remote_name):
        """Upload the file `local_name` to GS as a blob named `remote_name`."""
        # We just upload regular files.
        if not local_name.is_file():
            _LOGGER.debug("Not attempting upload - not a file %s", local_name)
            return
        if local_name.is_symlink():
            _LOGGER.debug("Not attempting upload - symlink %s", local_name)
            return

        blob = self._gs_bucket.blob(remote_name, chunk_size=(1024 * 1024 * 100))

        if do_not_gzip(local_name):
            target_file_path = local_name
        else:
            temp_zipped_file_path = self._gzip_file(local_name)
            target_file_path = temp_zipped_file_path
            blob.content_encoding = "gzip"

        try:
            retry_call(
                blob.upload_from_filename,
                fargs=[str(target_file_path)],
                fkwargs={"client": self._client},
                exceptions=(
                    requests.exceptions.ConnectionError,
                    urllib3.exceptions.ProtocolError,
                ),
                tries=20,
                delay=1,
                backoff=1.25,
            )
        finally:
            try:
                os.remove(temp_zipped_file_path)
            except UnboundLocalError:
                # If remove operation fails with unbound error, zip file was never created, pass.
                pass

    @property
    def bucket_name(self):
        return self._bucket_name
