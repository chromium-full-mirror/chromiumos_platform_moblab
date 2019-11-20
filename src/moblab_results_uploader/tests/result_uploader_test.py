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
@mock.patch('moblab_common.lock_util.file_lock', new=mock.MagicMock())
@mock.patch('pathlib.Path.write_text', new=mock.Mock())
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

    with mock.patch('pathlib.Path.read_text') as m_read:
        m_read.return_value = 'READY'
        result = await uploader.try_upload_dir(test_result)
    assert result.uploaded is True


@pytest.mark.asyncio
@mock.patch('moblab_common.lock_util.file_lock', new=mock.MagicMock())
@mock.patch('pathlib.Path.write_text', new=mock.Mock())
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

    with mock.patch('pathlib.Path.read_text') as m_read:
        m_read.return_value = 'READY'
        result = await uploader.try_upload_dir(test_result)
    assert result.uploaded is False


@pytest.mark.asyncio
@mock.patch('moblab_common.lock_util.file_lock')
@mock.patch('moblab_common.pubsub_client.PubSubBasedClient')
async def test_post_uploading(m_pubsub, m_lock):
    post_uploading = result_uploader.PostUploading('test_bucket')
    test_result = mock.Mock(pubsub_when_uploaded=True,
                            abs_path=pathlib.Path('/abs/path/to/test'))
    upload_result = mock.Mock(test_result=test_result,
                              test_result_gs_path='gs/path/to/file')
    with mock.patch('pathlib.Path.open') as m_open:
        await post_uploading.process(upload_result)
        assert m_open.called
        assert m_pubsub.called


@pytest.mark.asyncio
@mock.patch('moblab_common.pubsub_client.PubSubBasedClient')
async def test_post_uploading__dryrun(m_pubsub):
    post_uploading = result_uploader.PostUploading('test_bucket', dry_run=True)
    test_result = mock.Mock(pubsub_when_uploaded=True)
    upload_result = mock.Mock(test_result=test_result,
                              test_result_gs_path='gs/path/to/file')
    with mock.patch('os.path.join') as os_path_join:
        await post_uploading.process(upload_result)
        assert not m_pubsub.called
        assert os_path_join.called
