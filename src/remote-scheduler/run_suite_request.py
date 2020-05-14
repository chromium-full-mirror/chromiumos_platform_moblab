# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Service that schedules commands on the moblab."""

from __future__ import print_function

import time
import json

import remote_request

try:
    from chromite.lib import cros_logging as logging
except ImportError:
    # pylint: disable=cros-logging-import
    import logging


class MoblabSuiteRunRequestWrapper(remote_request.MoblabRemoteRequest):
    """Encapsulates all the information required to run a suite on moblab."""

    def __init__(self,
                 unique_id=None,
                 board=None,
                 build=None,
                 priority=None,
                 suite=None,
                 min_duts=0,
                 suite_args='',
                 model=None,
                 test_args='',
                 expires_at_sec_utc=None,
                 pubsub_message_id=None,
                 proto=None):
        """Class constructor.

            Construct the suite request either from the params or from
            a proto that contains all the params.

            unique_id (string, optional): Defaults to None. The unique
                identifier for this request, if None a new identifier will be
                generated.
            board (string, optional): Defaults to None. The board to run the
                suite with.
            build (string, optional): Defaults to None. The build number to
                run e.g. R75-12055.0.0
            priority (int, optional): Defaults to None. The priority of the
                request, lower number is higher priority.
            suite (string, optional): Defaults to None. The name of the
                suite to run e.g. cts_P
            min_duts (int, optional): Minimun number of active DUT's attached
                with the correct board/model before the suite will run.
            suite_args (string, optional): Defaults to None.  key=value pairs
                delimited by newlines.
            model (string, optional): Defaults to None. The model to run the
                suite on.
            test_args (string, optional): Defaults to None. key=value pairs
                delimited by newlines.
            expires_at_sec_utc (string, optional): Defaults to None. If set
                a time in UTC at which this command will be ignored.
            proto (object, optional): Defaults to None.Allows construction of
                this object from the values in a the proto equivalent.
        """

        if proto:
            unique_id = proto.base.unique_id
            board = proto.base.board
            build = proto.build
            priority = proto.base.priority
            suite = proto.suite
            min_duts = proto.base.min_duts
            suite_args = proto.suite_args
            test_args = proto.test_args
            expires_at_sec_utc = proto.base.expires_at_sec_utc
            model = proto.base.model
            pubsub_message_id = proto.base.pubsub_message_id

        super(MoblabSuiteRunRequestWrapper, self).__init__(unique_id)

        self.board = board
        self.build = build
        self.priority = priority
        self.suite = suite
        self.min_duts = min_duts
        self.suite_args = suite_args
        self.model = model
        self.test_args = test_args
        self.expires_at_sec_utc = expires_at_sec_utc
        self.pubsub_message_id = pubsub_message_id

        if not self.model:
            self.model = self.board

    def __str__(self):
        """Return a formatted string of the information held in this object.

        Returns:
            str: Formatted string representing this object.
        """

        return (
            'unique_id=%s, build=%s, board=%s, suite=%s, model=%s, priority=%s,'
            ' min_duts=%s' % (self.unique_id, self.build, self.board,
                              self.suite, self.model, self.priority,
                              self.min_duts))

    def copy_to_proto(self, proto):
        """Copy the object data into a proto format.

        Args:
            proto (object): Proto object to copy the data into.
        """
        proto.base.unique_id = self.unique_id
        proto.build = self.build
        proto.base.board = self.board
        proto.base.priority = self.priority
        proto.suite = self.suite
        proto.base.min_duts = self.min_duts
        proto.base.expires_at_sec_utc = self.expires_at_sec_utc
        if self.pubsub_message_id:
            proto.base.pubsub_message_id = self.pubsub_message_id
        if self.model:
            proto.base.model = self.model
        if self.suite_args:
            proto.suite_args = json.dumps(self.suite_args)
        if self.test_args:
            proto.test_args = json.dumps(self.test_args)

    def can_be_executed(self, attached_boards):
        """Check to see if a request can be executed at this time.

        Args:
            attached_boards (dict): Mapping of board model number to the
            number of available DUT's

        Returns:
            [bool]: True if the task can run False if this Moblab is not
            currently capable of running the request.
        """

        board_model = '%s.%s' % (self.board, self.model)
        if board_model not in attached_boards.keys():
            logging.debug('No attached boards for %s', board_model)
            return False

        if self.min_duts and self.min_duts > attached_boards[board_model]:
            logging.info(('Not enough DUTs board: %s attached: %d'
                          ' required: %d'), board_model,
                         attached_boards[board_model], self.min_duts)
            return False

        #TODO(haddowk) move the check that the build can be staged to here.
        return True

    def execute(self, devserver_connector, autotest_connector):
        """Execute a run suite command on this moblab.

        Args:
            devserver_connector (object): Instanciated API object to access the
                devserver.
            autotest_connector (object): Instanciated API object to access the
                autotest server.
        """

        # if the request has expired then don't run the suite
        if self.expires_at_sec_utc and int(
                time.time()) > self.expires_at_sec_utc:
            return

        if devserver_connector.stage_build(self.board, self.build):
            autotest_connector.run_suite(
                board=self.board,
                build=self.build,
                builds=[],
                suite=self.suite,
                suite_timeout_mins=60*24*21,
                model=self.model,
                suite_args=self.suite_args,
                test_args=self.test_args)
