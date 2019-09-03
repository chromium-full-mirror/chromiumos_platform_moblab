#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Service that runs on moblab and checks to see if any tests are to be
# scheduled for this device.
"""Service that regularly checks for remote commands and executes them."""
from __future__ import print_function

import argparse
import datetime
import os
import sys
import time
import functools
from collections import defaultdict

# pylint: disable=no-name-in-module, import-error
from google.cloud import exceptions as cloud_exceptions, storage
# pylint: disable=no-name-in-module, import-error
from google.auth import exceptions as auth_exceptions

from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common import devserver_connector
from moblab_common import versioned_upload

import remote_requests
import scheduler_common

from chromite.lib import cros_logging as logging

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS',
                      '/home/moblab/.service_account.json')


class MoblabTestScheduler(object):
    """Service that regularly checks for remote commands and executes them."""

    def __init__(self):
        """Constructor."""
        self.storage_client = storage.Client()
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector)
        self.requests = remote_requests.MoblabRemoteRequests()
        self.moblab_bucket_name = self.config_connector.get_cloud_bucket()
        logging.info('Using bucket: %s', self.moblab_bucket_name)
        self.devserver_connector = devserver_connector.DevserverConnector(
            self.moblab_bucket_name)
        self.moblab_id = open(os.environ['HOME'] + '/.moblab_id').readlines()

    def get_executed_commands(self):
        """Get the list of commands that have already been executed.

        Returns:
            list: A list of strings, each string being a unique id of an
                executed command.
        """
        return scheduler_common.get_executed_commands(self.storage_client,
                                                      self.moblab_bucket_name)

    def obtain_lock(self, request):
        """Create lock file for the remote command request.

        By successfully creating an object in cloud storage with version 0 you
        are guaranteed to be the only process able to create that file.

        The contents of the file are just for debugging, possibly future
        reporting.

        Args:
            request: a MoblabRemoteRequest.

        Returns:
            bool: True if the lock was successfully obtained otherwise false.
        """
        logging.debug('Obtaining lock %s' % request.unique_id)
        blob = self.storage_client.bucket(self.moblab_bucket_name).blob(
            '%s/%s' % (scheduler_common.SCHEDULE_DIR, request.unique_id))
        if blob.exists():
            logging.debug('Lock already %s exists' % request.unique_id)
            return False
        contents = 'Lock date %s\nRequest %s\nMoblab Id: %s' % (
            datetime.datetime.utcnow(), request, self.moblab_id)
        try:
            versioned_upload.upload_from_string(blob, contents, 0)
        except cloud_exceptions.NotFound:
            return False
        return True

    def get_available_hosts(self):
        """Get the board.model string for DUT's that can run tests.

        Make a list of the configured DUT's on this device that are working
        and availabe to run tests.

        Returns:
            dict: mapping of board.model to number of working configured devices
                connected to this moblab.
        """
        available_hosts = defaultdict(int)
        hosts = self.afe_connector.get_connected_devices()
        for host in hosts:
            if host['status'] != 'Ready' or host['locked']:
                logging.debug('Host not ready or locked')
                continue
            labels = host['labels']

            board = None
            model = None
            for label in labels:
                if label.startswith('model:'):
                    model = label.split(':')[1]
                    continue
                if label.startswith('board:'):
                    board = label.split(':')[1]
                    continue
            if not model:
                model = board
            identifier = '%s.%s' % (board, model)
            available_hosts[identifier] += 1
        logging.debug(available_hosts)
        return available_hosts

    # Get the required build to run
    def get_next_command_to_run(self):
        """Go through the list of commands and figure out the best one to run.

        Returns:
            object: Object describing the request to be executed or None if
                there is no request able to be scheduled.
        """
        attached_boards = self.get_available_hosts()
        if not attached_boards:
            return None
        blob = storage.Blob(scheduler_common.SCHEDULE_FILENAME,
                            self.storage_client.bucket(self.moblab_bucket_name))
        self.requests.load_requests_from_gcs(blob)
        executed = self.get_executed_commands()

        def has_been_executed(executed, request):
            if request.unique_id in executed:
                logging.debug('Rejecting request %s as executed',
                              request.unique_id)
                return False
            return True

        def can_be_executed(attached_boards, request):
            return request.can_be_executed(attached_boards)

        # Filter out all commands that can or should not run on this moblab.
        self.requests.filter_requests(
            functools.partial(has_been_executed, executed))
        self.requests.filter_requests(
            functools.partial(can_be_executed, attached_boards))
        # TODO(haddowk) Filter out / remove expired tasks.
        self.requests.sort_requests()

        # return the first highest priority command to run.
        return self.requests.get_request(index=0)

    def setup_logging(self, level):
        """Enable the correct level of logging.

        Args:
            level (int): One of the predefined logging levels, e.g loging.DEBUG
        """
        logging.getLogger().handlers = []
        logging.getLogger().setLevel(level)
        fh = logging.FileHandler('/var/log/moblab_remote_schedule.log')
        fh.setLevel(level)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logging.getLogger().addHandler(fh)

    def parse_arguments(self, argv):
        """Creates the argument parser."""
        parser = argparse.ArgumentParser(description=__doc__)

        parser.add_argument(
            '-s',
            '--single_run',
            action='store_true',
            help='Run the scheduler one time and then exit.')
        parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='Turn on debug logging.')
        return parser.parse_args(argv)

    def execute_remote_commands(self, argv):
        """Loop forever, waiting for new commands to be executed on this device.

        Args:
            argv (list): Arguments passed in from the command line.

        Returns:
            bool: False if the scheduler is not enabled on this device.
        """
        is_enabled = self.config_connector.is_remote_task_scheduler_enabled()
        delay_mins = self.config_connector.get_remote_task_scheduler_tick_delay(
        )
        debug_enabled = self.config_connector.is_remote_task_debug_enabled()

        options = self.parse_arguments(argv)

        logging_severity = logging.INFO
        if options.verbose or debug_enabled:
            logging_severity = logging.DEBUG
        self.setup_logging(logging_severity)

        if not is_enabled:
            logging.info('The scheduler is not enabled')
            return False

        logging.info('Starting scheduler: tick delay: %s' % delay_mins)

        while True:
            request = self.get_next_command_to_run()
            if request:
                if self.obtain_lock(request):
                    logging.info('Executing request. %s', request.unique_id)
                    #TODO - return an enum SUCCESS/FAIL/RETRY.
                    request.execute(self.devserver_connector,
                                    self.afe_connector)
            else:
                logging.debug('No requests to run.')
            if options.single_run:
                break
            logging.debug('Sleeping for %d mins', delay_mins)
            time.sleep(delay_mins * 60)


if __name__ == '__main__':
    try:
        scheduler = MoblabTestScheduler()
    except auth_exceptions.DefaultCredentialsError as e:
        logging.exception('Failed to start remote scheduler, %s', str(e))
        sys.exit(0)
    scheduler.execute_remote_commands(sys.argv[1:])
