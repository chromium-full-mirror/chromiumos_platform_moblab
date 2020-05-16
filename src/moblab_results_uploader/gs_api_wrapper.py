# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# TODO(guocb) Move this wrapper to moblab_common and integreated with
# moblab_common/versioned_upload.py

"""A wrapper of Google Cloud Storage API."""

import logging  # pylint: disable=cros-logging-import
import os

from google.cloud import exceptions as gcp_exceptions
from google.cloud import storage as gs


ENV_GOOGLE_APP_CREDENTIALS = 'GOOGLE_APPLICATION_CREDENTIALS'
_LOGGER = logging.getLogger(__name__)


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
    _LOGGER.info('Verify the access to Google Storage.')
    if not credentials_file:
        raise GsAccessError('No credential file specified.')
    os.environ[ENV_GOOGLE_APP_CREDENTIALS] = credentials_file
    client = gs.Client()
    try:
        bucket = client.get_bucket(gs_bucket)
    except (gcp_exceptions.Forbidden, gcp_exceptions.NotFound) as err:
        raise GsAccessError(str(err))

    # Test the write permission.
    if bucket.test_iam_permissions(['storage.objects.create']):
        return bucket

    raise GsAccessError(
        "You don't have write permission to the bucket:{}".format(gs_bucket))


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
        self._gs_bucket = _get_gs_bucket(self._bucket_name, self._credentials_file)

    def upload_from_filename(self, *, local_name, remote_name):
        """Upload the file `local_name` to GS as a blob named `remote_name`."""
        # We just upload regular files.
        if not local_name.is_file():
            return
        if local_name.is_symlink():
            return
        blob = self._gs_bucket.blob(remote_name)
        blob.upload_from_filename(str(local_name))

    @property
    def bucket_name(self):
        return self._bucket_name
