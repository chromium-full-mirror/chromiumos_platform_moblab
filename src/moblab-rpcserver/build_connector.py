# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""
from __future__ import print_function

try:
    from chromite.lib import cros_logging as logging
except ImportError:
    import logging

# pylint: disable=no-name-in-module, import-error
from google.cloud import storage
# pylint: disable=no-name-in-module, import-error
from google.auth import exceptions as auth_exceptions


class MoblabBuildConnectorException(Exception):
    pass


class MoblabBuildConnector(object):
    """TODO ADD DOC"""

    def __init__(self, moblab_bucket_name, storage_client=None):
        if not moblab_bucket_name:
            raise MoblabBuildConnectorException('Missing bucket name')
        self.moblab_bucket_name = moblab_bucket_name
        if storage_client:
            self.storage_client = storage_client
        else:
            try:
                self.storage_client = storage.Client()
            except auth_exceptions.DefaultCredentialsError as e:
                logging.info('No credentials loaded')
                raise MoblabBuildConnectorException('Invalid Credentials')

    def get_partial_object_path(self, prefix, delimiter):
        blob_itr = self.storage_client.bucket(
            self.moblab_bucket_name).list_blobs(
                prefix=prefix, delimiter=delimiter)
        # pylint: disable=pointless-statement
        [None for _ in blob_itr]
        return [partial_path for partial_path in blob_itr.prefixes]

    def get_boards_available(self):
        possible_boards = self.get_partial_object_path(None, '/')
        possible_boards = [
            board for board in possible_boards if board.endswith('-release/')
        ]
        return [board[:-len('-release/')] for board in possible_boards]

    def get_milestones_available(self, board):
        prefix = '%s-release/R' % board
        milestones = self.get_partial_object_path(prefix, '-')
        return [milestone[len(prefix) - 1:-1] for milestone in milestones]

    def get_builds_for_milestone(self, board, milestone):
        prefix = '%s-release/%s-' % (board, milestone)
        builds = self.get_partial_object_path(prefix, '/')
        return [build[len(prefix):-1] for build in builds]
