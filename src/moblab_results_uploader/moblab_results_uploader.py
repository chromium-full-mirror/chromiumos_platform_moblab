# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A moblab dedicated service to upload test results to GS bucket."""



import argparse
import logging
import logging.handlers as logging_handlers
import pathlib
import sys

import yaml

import cmd_run
import cmd_try_file_filter
import result_file_filter

from moblab_common import config_connector

_LOG_FILE_BACKUP_COUNT = 14
_LOGGER = logging.getLogger(pathlib.Path(__file__).stem)


def _logging_file_type(logfile_path):
    """Wrap the input file path as a logging handler object."""
    try:
        return logging_handlers.TimedRotatingFileHandler(
            logfile_path, when='D', interval=1,
            backupCount=_LOG_FILE_BACKUP_COUNT)
    except PermissionError as err:
        raise argparse.ArgumentTypeError(str(err))


def _setup_logging(handler):
    """Set up logging.

    Args:
        handler: The logging handler object.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(filename)s:%(lineno)d %(levelname)s: %(message)s'))
    # Some code runs before this function may have created some handler and we
    # don't want them.
    logger.handlers = [handler]

    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('moblab_common').setLevel(logging.WARNING)

def _results_filter_type(config_file_path):
    """Load the results filter configuration."""
    try:
        with open(config_file_path) as config_file:
            filters = yaml.load(config_file, Loader=yaml.BaseLoader)
    except (PermissionError, FileNotFoundError) as err:
        raise argparse.ArgumentTypeError(str(err))

    try:
        result_file_filter.filters_sanity_check(filters)
    except result_file_filter.FilterConfigError as err:
        raise argparse.ArgumentTypeError(str(err))
    return filters


# pylint: disable=inconsistent-return-statements
def _parse_args(argv):
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-l', '--log-file', default=logging.StreamHandler(sys.stdout),
        type=_logging_file_type, dest='log_handler',
        help='The log file path. Default is stdout.'
    )
    parser.add_argument(
        '-f', '--uploading-filter-config-file',
        type=_results_filter_type, dest='uploading_filter_config', default=[],
        metavar='UPLOADING_FILTER_CONFIG_FILE',
        help='The path of a YAML file which configures the uploading filters '
        'for different test suites.'
    )

    subparsers = parser.add_subparsers(
        title='Subcommands',
        help='Subcommands supported. One and only one of them can be used.')

    cmd_run.add_arguments(subparsers)
    cmd_try_file_filter.add_arguments(subparsers)

    args = parser.parse_args(argv)

    if hasattr(args, 'post_parse_args'):
        args.post_parse_args(args)

    # TODO(guocb) Use 'required' flag of argparse after upgrade to Python 3.7.
    if hasattr(args, 'func'):
        return args

    parser.error('Please specify one of the subcommands.')


def main(argv):
    """Main entry of the service."""
    args = _parse_args(argv)
    _setup_logging(args.log_handler)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
