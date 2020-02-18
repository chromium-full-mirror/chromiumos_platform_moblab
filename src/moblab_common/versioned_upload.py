# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Work around until API allow setting of preconditions.

See https://github.com/googleapis/google-cloud-python/issues/4490
for full details, we need to be able to set the generation of
files when using the cloud storage as task locking solution,
setting the generation to 0 guarantees only a single system/process
can create the file.
"""

# pylint: disable=no-name-in-module, import-error
from google.cloud import storage

# pylint: disable=protected-access
DEFAULT_MULTIPART_URL_TEMPLATE = storage.blob._MULTIPART_URL_TEMPLATE
DEFAULT_RESUMABLE_URL_TEMPLATE = storage.blob._RESUMABLE_URL_TEMPLATE


def upload_from_string(blob, data, version=None):
    """Upload a string to a GCS blob, optionally setting the version.

    https://cloud.google.com/storage/docs/generations-preconditions#_JSONAPI
    explains how version preconditions work.

    Args:
        blob (storage.Blob): Google cloud storage object.
        data (string): The data to write to the blob.
        version (integer, optional): Defaults to None. Set the generation
            precondition to this version.
    """

    if version:
        storage.blob._MULTIPART_URL_TEMPLATE = ('%s&ifGenerationMatch=%d' % (
            DEFAULT_MULTIPART_URL_TEMPLATE, version))
        storage.blob._RESUMABLE_URL_TEMPLATE = ('%s&ifGenerationMatch=%d' % (
            DEFAULT_RESUMABLE_URL_TEMPLATE, version))
    blob.upload_from_string(data)
    storage.blob._MULTIPART_URL_TEMPLATE = DEFAULT_MULTIPART_URL_TEMPLATE
    storage.blob._RESUMABLE_URL_TEMPLATE = DEFAULT_RESUMABLE_URL_TEMPLATE
