# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for `gs_api_wrapper`."""

from __future__ import print_function

import pathlib
import tempfile
import unittest

import pytest

import gs_api_wrapper


@pytest.mark.network
def test_uploading_blob(gs_bucket, credentials_file):
    """Test uploading a file."""
    gs = gs_api_wrapper.GsApiWrapper(gs_bucket, credentials_file)
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"Some test data.\n")
        f.seek(0)
        gs.upload_from_filename(
            local_name=pathlib.Path(f.name), remote_name=f.name
        )


class GsApiWrapperTest(unittest.TestCase):
    """Unit test case for Google Storage uploader."""

    @pytest.mark.network
    def test_credential(self):
        with self.assertRaises(gs_api_wrapper.GsAccessError):
            gs_api_wrapper.GsApiWrapper("FAKE_BUCKET", None)
