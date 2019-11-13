# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""The implementation of subcommand `run`."""

from __future__ import print_function

import argparse
import asyncio
import datetime
import logging  # pylint: disable=cros-logging-import
import os
import pathlib
import shutil

import yaml

from moblab_common import afe_connector
from moblab_common import config_connector

import gs_api_wrapper
import processing_step
import result_dir_status
import result_file_filter
import result_uploader
import test_result_registry as test_result_registry_module

SUB_COMMAND_NAME = 'run'
_LOGGER = logging.getLogger(pathlib.Path(__file__).stem)

_DEFAULT_UPLOAD_TIMEOUT = datetime.timedelta(days=3)
_DEFAULT_MIN_AGE_TO_UPLOAD = datetime.timedelta(days=0)
_DEFAULT_MIN_AGE_TO_PRUNE = datetime.timedelta(days=7)

_RUN_INTERVAL = datetime.timedelta(minutes=1)


async def _enumerate_test_results(test_result_registry, *, next_step):
    """Enumerate all test results registered."""
    for registry_entry in test_result_registry:
        for cls in registry_entry.classes:
            root_dir = registry_entry.root_dir
            for d in root_dir.glob(cls.GLOB_PATTERN):
                test_result = cls(root_dir=root_dir,
                                  relative_path=d.relative_to(root_dir))
                await next_step(test_result)
                _LOGGER.info('Found a test result: %s', test_result)

    return None


async def _prune_test_result(test_result):
    """Check the `test_result` and try to prune it if we should."""
    # Remove all other files/directories first, and remove the marker file
    # last.
    _LOGGER.debug('Removing test result %s', test_result)
    loop = asyncio.get_event_loop()
    rm_tasks = []
    for d in test_result.abs_path.iterdir():
        if d.is_dir():  # Remove all subdirectories.
            rm_tasks.append(loop.run_in_executor(None, shutil.rmtree, d))
        elif d.name != result_dir_status.MARKER_FILE:
            # Remove all files except the marker.
            rm_tasks.append(loop.run_in_executor(None, d.unlink))
    await asyncio.wait(rm_tasks)
    await loop.run_in_executor(None, shutil.rmtree, test_result.abs_path)
    _LOGGER.debug('Removing done: %s', test_result)


async def _async_prune(args, registry):
    """Scan and prune all EXPIRED test results."""
    status_checker = result_dir_status.ResultStatusChecker(
        min_age_to_upload=args.min_age_to_upload,
        min_age_to_prune=args.min_age_to_prune
    )
    status_filter = result_dir_status.StatusFilter(
        result_dir_status.Status.EXPIRED)

    # Steps needed to prune a result directory:
    # check status -> for each EXPIRED directories -> prune it.
    status_checker.next_step = status_filter.filter
    status_filter.next_step = _prune_test_result

    while True:
        await _enumerate_test_results(registry, next_step=status_checker.check)
        if args.once:
            break
        await asyncio.sleep(_RUN_INTERVAL.total_seconds())


async def _async_upload(args, registry):
    """Scan and upload all 'READY' test results."""
    status_checker = result_dir_status.ResultStatusChecker(
        min_age_to_upload=args.min_age_to_upload,
        min_age_to_prune=args.min_age_to_prune
    )
    status_filter = result_dir_status.StatusFilter(
        result_dir_status.Status.UPLOADING)
    uploader = result_uploader.Uploader(
        timeout=args.upload_timeout,
        gs_api=gs_api_wrapper.GsApiWrapper(
            args.gs_bucket, args.credentials_file))
    file_filter = result_file_filter.ResultFileFilter(
        filter_config=args.uploading_filter_config)

    # The processing flow is:
    # get status -> for each ready directory -> list all files -> apply file
    # filter -> put to uploading queue -> wait queue joining -> post uploading
    # processing.
    post_uploading = result_uploader.PostUploading(args.gs_bucket)
    status_checker.next_step = status_filter.filter
    status_filter.next_step = processing_step.DataProcessFlow(
        uploader.try_upload_dir,
        post_uploading.process,
    )
    uploader.next_step = file_filter.filter_files
    file_filter.next_step = uploader.uploading_queue.put

    consumers = [
        asyncio.ensure_future(uploader.upload_files())
        for _ in range(args.jobs)
    ]
    while True:
        await _enumerate_test_results(registry, next_step=status_checker.check)
        if args.once:
            break
        await asyncio.sleep(_RUN_INTERVAL.total_seconds())

    for consumer in consumers:
        consumer.cancel()


def _accessible_file_type(file_path):
    """Check if input is an accessible file."""
    if not file_path:
        raise argparse.ArgumentTypeError('No value specified.')

    try:
        with open(file_path):
            pass
        return file_path
    except (FileNotFoundError, PermissionError) as err:
        raise argparse.ArgumentTypeError(err)


def add_arguments(parent_parser):
    """Add arguments for subcommand 'run'.

    Args:
        parent_parser: The argparse.ArgumentParser object to add arguments.
    """
    parser = parent_parser.add_parser(
        SUB_COMMAND_NAME,
        help='Scan, upload and prune the test result directories.')
    parser.add_argument(
        '--once', action='store_true', help='Just run once and exit.')
    parser.add_argument(
        '-n', '--dry-run', action='store_true',
        help='Dry run mode: just print out directories processed. Only valid '
        'when specified with option --once.'
    )
    parser.add_argument(
        '-j', '--jobs', type=int, default=1,
        help='Allow N jobs run simultaneously to work.'
    )
    parser.add_argument(
        '--gs-bucket',
        default=config_connector.MoblabConfigConnector(
            afe_connector.AFEConnector()).get_cloud_bucket(),
        help='The Google Storage Bucket to upload (without "gs://" prefix). '
        'Default is reading from Autotest config file, i.e. %(default)s'
    )

    parser.add_argument(
        '--credentials-file',
        default=os.environ.get(gs_api_wrapper.ENV_GOOGLE_APP_CREDENTIALS, ''),
        type=_accessible_file_type,
        help='Google cloud application credentials file. Default is the value '
        'of environment variable {}, i.e. "%(default)s".'.format(
            gs_api_wrapper.ENV_GOOGLE_APP_CREDENTIALS)
    )

    parser.add_argument(
        '--timeout-days', type=lambda x: datetime.timedelta(days=float(x)),
        default=_DEFAULT_UPLOAD_TIMEOUT, dest='upload_timeout',
        help='The timeout time in days (can be a float number) to give up the '
        'uploading (default: %(default)s).'
    )
    parser.add_argument(
        '--min-age-to-upload', type=lambda x: datetime.timedelta(days=float(x)),
        default=_DEFAULT_MIN_AGE_TO_UPLOAD,
        help='Minimum job age in days (can be a float number) before a result '
        'can be uploaded, but not removed from local storage '
        '(default: %(default)s).'
    )
    parser.add_argument(
        '--min-age-to-prune', type=lambda x: datetime.timedelta(days=float(x)),
        default=_DEFAULT_MIN_AGE_TO_PRUNE,
        help='Minimum job age in days (can be a float number) before a result '
        'can be removed from local storage (default: %(default)s).'
    )

    parser.set_defaults(func=run)


def run(args, test_result_registry=None):
    """Main logic to scan, upload and prune the test results.

    Args:
        args: The command line arguments specified.
        test_result_registry: A list of TestResultRegisteryEntry which has
            needed test result directory information.
    """
    if not args.gs_bucket:
        _LOGGER.error('GS Bucket not specified.')
        return
    _LOGGER.debug('arguments: %s', args)
    _LOGGER.info('Start to scan, upload and prune test results.')

    registry = test_result_registry or test_result_registry_module.REGISTRY
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(asyncio.gather(_async_upload(args, registry),
                                               _async_prune(args, registry)))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
