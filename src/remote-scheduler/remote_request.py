# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Base class for all moblab remote request implementations."""

from __future__ import print_function

import uuid
import sys


class MoblabRemoteRequest(object):
    """Abstract base class for all moblab remote requests."""

    def __init__(self, unique_id=None, priority=None):
        """Base class for all Moblab remote requests.

        Args:
            unique_id (string): If you are creating a request object
                from a serialized defintions (proto) then supply the unique id
                otherwise let the class generate this id for all new requests.
            priority (int): The priority of this request, lower number is higher
                priority.
        """
        if not unique_id:
            unique_id = uuid.uuid4().hex
        self.unique_id = unique_id
        if not priority:
            priority = sys.maxsize
        self.priority = priority
        self.expires_at_sec_utc = sys.maxsize

    def copy_to_proto(self, proto):
        """Generate a proto from the data in this object.

        Args:
            proto (object): An instance of proto definition of this request
            object.

        Raises:
            NotImplementedError: Derived classes must supply an implementation.
        """
        raise NotImplementedError

    def execute(self, devserver_connector, autotest_connector):
        """The code that executes a request on Moblab.

        Each request type should implement the necessary code to
        run perform that command on moblab.

        Args:
            devserver_connector (object): Access to the devserver API
            autotest_connector (object): Access to the autotest API

        Raises:
            NotImplementedError
        """

        raise NotImplementedError

    def can_be_executed(self, attached_boards):
        """A check to see if the command is eligible for execution.

        Based on the boards availabe return True if the command
        can be executed, otherwise False.

        Args:
            attached_boards (string list): A list of board.model

        Raises:
            NotImplementedError
        """

        raise NotImplementedError
