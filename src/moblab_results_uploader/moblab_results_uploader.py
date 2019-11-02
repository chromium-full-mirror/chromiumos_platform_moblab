# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A moblab dedicated service to upload test results to GS bucket."""

from __future__ import print_function

import asyncio
import argparse
import datetime
import logging.handlers as logging_handlers
import logging  # pylint: disable=cros-logging-import
import pathlib
import shutil
import sys

import autotest_result
import test_result_registry as test_result_registry_module


_LOG_FILE_BACKUP_COUNT = 14
_LOGGER = logging.getLogger(pathlib.Path(__file__).stem)

_DEFAULT_UPLOAD_TIMEOUT = datetime.timedelta(days=3)
_DEFAULT_MIN_AGE_TO_UPLOAD = datetime.timedelta(days=0)
_DEFAULT_MIN_AGE_TO_PRUNE = datetime.timedelta(days=7)

_RUN_INTERVAL = datetime.timedelta(minutes=1)

_TEST_RESULT_STATE_FILE = '.uploader_status'


async def enumerate_test_results(test_result_registry, *, next_step):
    """Enumerate all test results registered."""
    for registry_entry in test_result_registry:
        for cls in registry_entry.classes:
            root_dir = registry_entry.root_dir
            for d in root_dir.glob(cls.GLOB_PATTERN):
                test_result = cls(root_dir=root_dir,
                                  relative_path=d.relative_to(root_dir))
                # TODO(guocb) Check if it's uploading or uploaded.
                await next_step(test_result)
                _LOGGER.info('Found a test result: %s', test_result)


async def upload_test_reuslt(test_result):
    """Upload method placeholder, do nothing for now."""
    _LOGGER.info('Uploading the result: %s', test_result)
    print('Uploading %s' % test_result)
    await asyncio.sleep(1)
    _LOGGER.info('Uploading done: %s', test_result)
    print('Uploading done: %s' % test_result)


async def try_upload_test_result(queue, timeout):
    """Get test result from `queue` and process it with `timeout`.

    Args:
        queue: An asyncio.Queue object to save all jobs.
        timeout: A datetime.timedelta object of timeout for each directory."""
    while True:
        test_result = await queue.get()
        if not test_result:
            _LOGGER.info('Exiting the results processing.')
            break
        _LOGGER.info('Try to upload %s', test_result)
        try:
            await asyncio.wait_for(upload_test_reuslt(test_result),
                                   timeout.total_seconds())
        except (asyncio.TimeoutError, KeyboardInterrupt) as err:
            _LOGGER.error(
                'Error occurs when uploading %s: %s', test_result, err)
            if err is KeyboardInterrupt:
                raise err
        queue.task_done()


async def prune_test_result(test_result):
    """Check the `test_result` and try to prune it if we should."""
    # Remove all other files/directories first, and remove the marker file
    # last.
    # TODO(guocb) Run in a thread executor to avoid freeze event loop.
    _LOGGER.debug('Removing test result %s', test_result)
    for d in test_result.abs_path.iterdir():
        if d.is_dir():  # Remove all subdirectories.
            shutil.rmtree(d)
        elif d.name != _TEST_RESULT_STATE_FILE:
            # Remove all files except the marker.
            d.unlink()
    shutil.rmtree(test_result.abs_path)
    _LOGGER.debug('Removing done: %s', test_result)


async def async_prune(args, registry):
    """Scan and prune all UPLOADED or EXPIRED test results."""
    to_prune = prune_test_result

    while True:
        await enumerate_test_results(registry, next_step=to_prune)
        if args.once:
            break
        await asyncio.sleep(_RUN_INTERVAL.total_seconds())


async def async_upload(args, registry):
    """Scan and upload all READY test results."""
    queue = asyncio.Queue()

    to_upload = queue.put
    consumer = asyncio.ensure_future(
        try_upload_test_result(queue, args.upload_timeout)
    )
    while True:
        await enumerate_test_results(registry, next_step=to_upload)
        await queue.join()
        if args.once:
            break
        await asyncio.sleep(_RUN_INTERVAL.total_seconds())

    consumer.cancel()


def run(args, test_result_registry=None):
    """Main logic to scan, upload and prune the test results.

    Args:
        args: The command line arguments specified.
        test_result_registry: A list of TestResultRegisteryEntry which has
            needed test result directory information.
    """
    _LOGGER.debug('arguments: %s', args)
    _LOGGER.info('Start to scan, upload and prune test results.')

    registry = test_result_registry or test_result_registry_module.REGISTRY
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(asyncio.gather(async_upload(args, registry),
                                               async_prune(args, registry)))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


def test_file_filter():
    """Test the file filter specified and list filtered result."""
    _LOGGER.info('Start to test the file filter.')


def logging_file_type(logfile_path):
    """Wrap the input file path as a logging handler object."""
    try:
        return logging_handlers.TimedRotatingFileHandler(
            logfile_path, when='D', interval=1,
            backupCount=_LOG_FILE_BACKUP_COUNT)
    # TODO (guocb) remove below pylint pragma once `cros lint` upgrade to
    # python 3.
    # pylint: disable=undefined-variable
    except (PermissionError, FileNotFoundError) as err:
        # pylint: enable=undefined-variable
        raise argparse.ArgumentTypeError(str(err))


def setup_logging(handler):
    """Set up logging.

    Args:
        handler: The logging handler object.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(handler)


def add_arguments_for_subcommand_run(parent_parser):
    """Add arguments for subcommand 'run'.

    Args:
        parent_parser: The argparse.ArgumentParser object to add arguments.
    """
    parser = parent_parser.add_parser(
        'run', help='Scan, upload and prune the test result directories.')
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
        '--gs-bucket', required=True,
        help='The Google Storage Bucket to upload (without "gs://" prefix).'
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


def add_arguments_for_subcommand_test_filter(parent_parser):
    """Add arguments for subcommand 'run'.

    Args:
        parent_parser: The argparse.ArgumentParser object to add arguments.
    """
    parser = parent_parser.add_parser(
        'test_filter', help='Test the file filter.')
    # TODO(guocb) add arguments for test_filter subcommand.
    parser.add_argument(
        '-d', '--dir',
        help='The directory to test the file filter.'
    )
    parser.set_defaults(func=test_file_filter)


def parse_args(argv):
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-l', '--log-file', default=logging.StreamHandler(sys.stdout),
        type=logging_file_type, dest='log_handler',
        help='The log file path. Default is stdout.'
    )

    subparsers = parser.add_subparsers(
        title='Subcommands',
        help='Subcommands supported. One and only one of them can be used.')

    add_arguments_for_subcommand_run(subparsers)
    add_arguments_for_subcommand_test_filter(subparsers)

    args = parser.parse_args(argv)

    # TODO(guocb) Use 'required' flag of argparse after upgrade to Python 3.7.
    if hasattr(args, 'func'):
        return args

    print('Please specify one of the subcommands.', file=sys.stderr, end='\n\n')
    parser.print_help()
    sys.exit(1)


def main(argv):
    """Main entry of the service."""
    args = parse_args(argv)
    setup_logging(args.log_handler)
    args.func(args)


if __name__ == '__main__':
    main(sys.argv[1:])
