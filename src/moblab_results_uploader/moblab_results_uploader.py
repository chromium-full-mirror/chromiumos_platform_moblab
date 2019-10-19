# -*- coding: utf-8 -*-

# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A moblab dedicated service to upload test results to GS bucket."""

from __future__ import print_function

import argparse
import datetime
# pylint: disable=cros-logging-import
import logging
import logging.handlers as logging_handlers
import sys

from chromite.lib import cros_logging as logging

_LOG_FILE_BACKUP_COUNT = 14
_DEFAULT_UPLOAD_TIMEOUT = datetime.timedelta(days=3)
_DEFAULT_MIN_AGE_TO_UPLOAD = datetime.timedelta(days=0)
_DEFAULT_MIN_AGE_TO_PRUNE = datetime.timedelta(days=7)


def run():
    """Main logic to scan, upload and prune the test results."""
    logging.info('Start to scan, upload and prune test results.')


def test_file_filter():
    """Test the file filter specified and list filtered result."""
    logging.info('Start to test the file filter.')


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
        '--timeout-days', type=lambda x: datetime.timedelta(days=int(x)),
        default=_DEFAULT_UPLOAD_TIMEOUT,
        help='The timeout time in days to give up the uploading '
        '(default: %(default)s).'
    )
    parser.add_argument(
        '--min-age-to-upload', type=lambda x: datetime.timedelta(days=int(x)),
        default=_DEFAULT_MIN_AGE_TO_UPLOAD,
        help='Minimum job age in days before a result can be uploaded, but '
        'not removed from local storage (default: %(default)s).'
    )
    parser.add_argument(
        '--min-age-to-prune', type=lambda x: datetime.timedelta(days=int(x)),
        default=_DEFAULT_MIN_AGE_TO_PRUNE,
        help='Minimum job age in days before a result can be removed from '
        'local storage (default: %(default)s).'
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
    args.func()


if __name__ == '__main__':
    main(sys.argv[1:])
