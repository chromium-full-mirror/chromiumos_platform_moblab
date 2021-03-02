# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for `gs_api_wrapper`."""

from __future__ import print_function
from unittest import mock

import pathlib
import pytest
import tempfile
import unittest

from gs_api_wrapper import do_not_gzip, GsAccessError, GsApiWrapper

class MockPath(type(pathlib.Path())):
    def __new__(cls, *args):
        return super(MockPath, cls).__new__(cls, *args)

    def __init__(self, path):
        super().__init__()

    def is_file(self):
        return True

    def is_symlink(self):
        return False

@pytest.mark.network
def test_uploading_blob(gs_bucket, credentials_file):
    """Test uploading a file."""
    gs = GsApiWrapper(gs_bucket, credentials_file)
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
        with self.assertRaises(GsAccessError):
            GsApiWrapper("FAKE_BUCKET", None)

    @mock.patch("gs_api_wrapper.gs")
    @mock.patch("gs_api_wrapper.retry_call")
    @mock.patch("gs_api_wrapper.gzip")
    @mock.patch("gs_api_wrapper.shutil")
    @mock.patch("gs_api_wrapper.os")
    @mock.patch("gs_api_wrapper.open")
    def test_upload_from_filename(self, mock_open, mock_os, mock_shutil, mock_gzip, mock_retry_call, mock_gs):
        gsApiWrapper = GsApiWrapper("FAKE_BUCKET", "fake_credentials_file")

        gsApiWrapper.upload_from_filename(local_name=MockPath("fake_upload_file.gz"), remote_name="fake_upload_file.gz")

        mock_retry_call.assert_called_once()

    def test_already_gzipped_files_not_compressed(self):
        self.assertTrue(do_not_gzip(pathlib.Path('file.gz')))
        self.assertTrue(do_not_gzip(pathlib.Path('file.tgz')))
        self.assertTrue(do_not_gzip(pathlib.Path('file.tar.gz')))
