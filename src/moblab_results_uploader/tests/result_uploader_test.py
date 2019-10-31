# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test cases for module `result_uploader`."""
from __future__ import print_function

import asyncio
import pathlib
from asynctest import mock

import pytest

import result_file_filter
import result_uploader


@pytest.mark.asyncio
@mock.patch('moblab_common.moblab_info.get_or_create_id',
            new=mock.Mock(return_value='moblab_id'))
@mock.patch('moblab_common.moblab_info.get_serial_number',
            new=mock.Mock(return_value='moblab_sn'))
async def test_upload_files():
    gs_api = mock.Mock()
    uploader = result_uploader.Uploader(timeout=None, gs_api=gs_api)
    test_result = mock.Mock()
    test_result.name = '123-moblab'
    test_result.abs_path = pathlib.Path('/root/to/test/123-moblab')
    files = ['file1', 'file2', 'file3']
    for f in files:
        await uploader.uploading_queue.put(result_file_filter.ResultFile(
            test_result=test_result, relative_path=f))

    task = asyncio.ensure_future(uploader.upload_files())
    # Ensure the test can be finished.
    try:
        await asyncio.wait_for(uploader.uploading_queue.join(), 1)
    finally:
        task.cancel()
    assert len(gs_api.upload_from_filename.call_args_list) == len(files)


@pytest.mark.asyncio
@mock.patch('moblab_common.moblab_info.get_or_create_id',
            new=mock.Mock(return_value='moblab_id'))
@mock.patch('moblab_common.moblab_info.get_serial_number',
            new=mock.Mock(return_value='moblab_sn'))
async def test_upload_dir__succeed():
    gs_api = mock.Mock()

    next_step = mock.CoroutineMock()
    timeout = mock.Mock()
    timeout.total_seconds.return_value = 1
    uploader = result_uploader.Uploader(timeout=timeout, gs_api=gs_api,
                                        next_step=next_step)

    test_result = mock.Mock()
    test_result.name = '123-moblab'
    test_result.abs_path = pathlib.Path('/root/to/test/123-moblab')

    result = await uploader.try_upload_dir(test_result)
    assert result.uploaded is True


@pytest.mark.asyncio
@mock.patch('moblab_common.moblab_info.get_or_create_id',
            new=mock.Mock(return_value='moblab_id'))
@mock.patch('moblab_common.moblab_info.get_serial_number',
            new=mock.Mock(return_value='moblab_sn'))
async def test_upload_dir__timeout():
    gs_api = mock.Mock()

    next_step = mock.CoroutineMock()
    timeout = mock.Mock(total_seconds=mock.Mock(return_value=0.5))

    uploader = result_uploader.Uploader(timeout=timeout, gs_api=gs_api,
                                        next_step=next_step)
    await uploader.uploading_queue.put('file1')

    test_result = mock.Mock()
    test_result.name = '123-moblab'
    test_result.abs_path = pathlib.Path('/root/to/test/123-moblab')

    result = await uploader.try_upload_dir(test_result)
    assert result.uploaded is False
