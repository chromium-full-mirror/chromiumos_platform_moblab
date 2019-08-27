#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Test script that generates remote commands for the moblab to execute.

from __future__ import print_function

from datetime import datetime
import argparse
import os
import sys
import time

# pylint: disable=no-name-in-module, import-error
from google.cloud import storage

import remote_requests
import run_suite_request
import scheduler_common
import build_connector

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS',
                      '%s/.service_account.json' % os.environ['HOME'])


class MoblabRemoteSchedulerCLI(object):

    def __init__(self, moblab_bucket_name):
        self.moblab_bucket_name = moblab_bucket_name
        self.storage_client = storage.Client()
        self.build_connector = build_connector.MoblabBuildConnector(
            moblab_bucket_name, self.storage_client)
        # TODO make this a time based cache
        self.executed = None

    def create_runsuite_command(self, board, model, suite, build, priority=2):
        suite_request = run_suite_request.MoblabSuiteRunRequest(
            board=board,
            build=build,
            model=model,
            priority=priority,
            suite=suite,
            min_duts=1,
            expires_at_sec_utc=int(time.time()) + 24 * 60 * 60)
        return suite_request

    def append_commands_to_list(self, new_commands):

        blob = storage.Blob(scheduler_common.SCHEDULE_FILENAME,
                            self.storage_client.bucket(self.moblab_bucket_name))
        commands = remote_requests.MoblabRemoteRequests()
        commands.load_requests_from_gcs(blob)
        for command in new_commands:
            commands.add_request(command)
        commands.save_requests_to_gcs(blob)

    def overwrite_command_list(self, new_commands):

        blob = storage.Blob(scheduler_common.SCHEDULE_FILENAME,
                            self.storage_client.bucket(self.moblab_bucket_name))
        new_commands.save_requests_to_gcs(blob)

    def display_all_command_status(self):
        blob = storage.Blob(scheduler_common.SCHEDULE_FILENAME,
                            self.storage_client.bucket(self.moblab_bucket_name))
        commands = remote_requests.MoblabRemoteRequests()
        commands.load_requests_from_gcs(blob)

        for request in commands.requests:
            is_executed, is_expired = self.get_request_status(request)
            status = 'pending'
            if is_executed:
                status = (
                    'executed\t\t\t%s' % scheduler_common.get_executed_contents(
                        self.storage_client, self.moblab_bucket_name,
                        request.unique_id).split('\n'))
            elif is_expired:
                status = 'expired'
            print(('Model: %s\t\t\t Build: %s\t\t Suite: %s\t\t\t'
                   ' Status: %s\t\t\tPubsub: %s') %
                  (request.model, request.build, request.suite, status,
                   request.pubsub_message_id))

    def get_input_from_list(self, options, question):
        i = 0
        for option in options:
            print('%d: %s' % (i, option))
            i += 1
        sels = input(question + ': ')
        if isinstance(sels) == int:
            return [options[sels]]
        selected_opts = []
        for sel in sels:
            selected_opts.append(options[sel])
        return selected_opts

    def interactive_queue_runsuite(self):
        boards = [
            board.split('-')[0]
            for board in self.build_connector.get_boards_available()
        ]
        selected_boards = self.get_input_from_list(boards,
                                                   'Pick a board number ')

        new_commands = []
        milestone = None
        build = None
        selected_suites = None

        for board in selected_boards:

            board_model_map = {
                'amd64-generic-cheets': ['rainier'],
                'cheza': ['cheza'],
                'cheza-freedreno': ['cheza'],
                'coral': [
                    'astronaut', 'babymega', 'babytiger', 'blacktip',
                    'blacktip360', 'blacktiplte', 'blue', 'bruce', 'coral',
                    'epaulette', 'lava', 'mako', 'nasher', 'nasher360',
                    'porbeagle', 'rabbid', 'robo', 'robo360', 'santa',
                    'thresher', 'whitetip', 'whitetip1', 'whitetip2'
                ],
                'grunt': [
                    'aleena', 'barla', 'careena', 'delan', 'grunt', 'kasumi',
                    'kasumi360', 'liara'
                ],
                'hatch': ['hatch', 'hatch_whl'],
                'kahlee': ['kahlee'],
                'kalista': ['karma'],
                'kukui': ['kukui'],
                'nami': [
                    'akali', 'akali360', 'bard', 'ekko', 'nami', 'pantheon',
                    'sona', 'syndra', 'vayne'
                ],
                'nautilus': ['nautilus', 'nautiluslte'],
                'octopus': [
                    'ampton', 'apel', 'bip', 'bluebird', 'bobba', 'bobba360',
                    'casta', 'fleex', 'grabbiter', 'korath', 'laser14', 'meep',
                    'mimrock', 'nospike', 'orbatrix', 'phaser', 'phaser360',
                    'sparky', 'sparky360', 'yorp'
                ],
                'rammus': ['shyvana'],
                'reef': [
                    'alan', 'basking', 'bigdaddy', 'electro', 'pyro', 'reef',
                    'sand', 'snappy'
                ],
                'sarien': ['arcada', 'arcada_signed', 'sarien'],
                'scarlet': ['dru', 'druwl', 'dumo', 'overkill'],
                'scarlet-arcnext': ['dru', 'druwl', 'dumo'],
                'soraka': ['soraka']
            }

            if not board in board_model_map:
                selected_models = [board]
            else:
                selected_models = self.get_input_from_list(
                    board_model_map[board], 'Pick a model number')

            for model in selected_models:
                if not milestone:
                    milestones = [
                        milestone.split('-')[0] for milestone in self
                        .build_connector.get_milestones_available(board)
                    ]
                    milestones.sort()
                    milestone = self.get_input_from_list(
                        milestones, 'Pick a milestone number')[0]

                if not build:
                    builds = self.build_connector.get_builds_for_milestone(
                        board, milestone)
                    builds.sort()
                    build = self.get_input_from_list(builds,
                                                     'Pick a build number ')[0]

                suites = ['cts_N', 'cts_P', 'gts', 'dummy_server']
                if not selected_suites:
                    selected_suites = self.get_input_from_list(
                        suites, 'Pick a suite number ')
                for suite in selected_suites:
                    new_commands.append(
                        self.create_runsuite_command(
                            board, model, suite, '%s-%s' % (milestone, build)))
        self.append_commands_to_list(new_commands)

    def remove_duplicates(self):
        blob = storage.Blob(scheduler_common.SCHEDULE_FILENAME,
                            self.storage_client.bucket(self.moblab_bucket_name))
        commands = remote_requests.MoblabRemoteRequests()
        commands.load_requests_from_gcs(blob)

        already_seen = []
        dup_count = 0
        deduped_commands = remote_requests.MoblabRemoteRequests()

        for request in commands.requests:
            key = '%s%s%s' % (request.model, request.build, request.suite)
            if key not in already_seen:
                already_seen.append(key)
                deduped_commands.add_request(request)
            else:
                dup_count += 1

        print('Removed %s duplicates' % dup_count)
        self.overwrite_command_list(deduped_commands)

    def remove_expired(self):
        blob = storage.Blob(scheduler_common.SCHEDULE_FILENAME,
                            self.storage_client.bucket(self.moblab_bucket_name))
        commands = remote_requests.MoblabRemoteRequests()
        commands.load_requests_from_gcs(blob)

        executed_and_pending_commands = remote_requests.MoblabRemoteRequests()

        for request in commands.requests:
            is_executed, is_expired = self.get_request_status(request)
            if is_executed or not is_expired:
                executed_and_pending_commands.add_request(request)

        self.overwrite_command_list(executed_and_pending_commands)

    def get_request_status(self, request):
        if not self.executed:
            self.executed = scheduler_common.get_executed_commands(
                self.storage_client, self.moblab_bucket_name)
        current_sec_utc = (
            datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        is_executed = request.unique_id in self.executed
        is_expired = request.expires_at_sec_utc < current_sec_utc
        return (is_executed, is_expired)

    def remove_all(self):
        empty = remote_requests.MoblabRemoteRequests()
        self.overwrite_command_list(empty)

    def run(self):
        self.display_all_command_status()
        while True:
            options = self.get_input_from_list([
                'List remote commands', 'Add remote suite command',
                'Remove duplicates', 'Remove expired', 'Remove all', 'Exit'
            ], 'Pick the number of a command')
            if options[0] == 'List remote commands':
                self.display_all_command_status()
            elif options[0] == 'Add remote suite command':
                self.interactive_queue_runsuite()
            elif options[0] == 'Remove duplicates':
                self.remove_duplicates()
            elif options[0] == 'Remove expired':
                self.remove_expired()
            elif options[0] == 'Remove all':
                self.remove_all()
            else:
                break


def _parse_arguments(argv):
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-b',
        '--bucket_name',
        type=str,
        default=None,
        help='What partners bucket to create commands in.')

    return parser.parse_args(argv)


def main(args):
    cmd_arguments = _parse_arguments(args)
    cli = MoblabRemoteSchedulerCLI(cmd_arguments.bucket_name)
    cli.run()


if __name__ == '__main__':
    main(sys.argv[1:])
