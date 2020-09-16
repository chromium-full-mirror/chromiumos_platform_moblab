# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""

try:
    from chromite.lib import cros_logging as logging
except ImportError:
    import logging

# pylint: disable=no-name-in-module, import-error
from google.cloud.storage import Client as GcsClient
# pylint: disable=no-name-in-module, import-error
from google.auth import exceptions as auth_exceptions


class MoblabBuildConnectorException(Exception):
    pass


class MoblabBuildConnector(object):
    """
        Contains logic for fetching build information from partner Google storage
        bucket.
    """

    def __init__(self, moblab_bucket_name, storage_client=None):
        if not moblab_bucket_name:
            raise MoblabBuildConnectorException('Missing bucket name')
        self.moblab_bucket_name = moblab_bucket_name
        if storage_client:
            self.storage_client = storage_client
        else:
            try:
                self.storage_client = GcsClient()
            except auth_exceptions.DefaultCredentialsError as e:
                logging.info('No credentials loaded')
                raise MoblabBuildConnectorException('Invalid Credentials')

    def _get_partial_object_path(self, prefix, delimiter):
        blob_itr = self.storage_client.bucket(
            self.moblab_bucket_name).list_blobs(
                prefix=prefix, delimiter=delimiter)
        # pylint: disable=pointless-statement
        [None for _ in blob_itr]
        return [partial_path for partial_path in blob_itr.prefixes]

    def get_boards_available(self):
        """Lists the available boards, aka build targets, in the partner bucket.

        Returns:
            List of strings representing boards.
        """
        possible_boards = self._get_partial_object_path(None, '/')
        possible_boards = [
            board for board in possible_boards if board.endswith('-release/')
        ]
        available_boards = [
            board[:-len('-release/')] for board in possible_boards
        ]
        available_boards.sort(key = lambda x: x)
        return available_boards

    def get_milestones_available(self, board):
        """Lists the available milestones in the partner bucket.

        Args:
            board (str): Build target name.
        Returns:
            List of strings representing build versions.
        """
        prefix = '%s-release/R' % board
        milestones = self._get_partial_object_path(prefix, '-')
        milestones = [
            milestone[len(prefix):-1] for milestone in milestones
        ]
        milestones.sort(key = lambda x: x)
        return milestones

    def get_builds_for_milestone(self, board, milestone):
        """Lists the available build versions in the partner bucket.

        Args:
            board (str): Build target name.
            milestone (str): The milestone number.
        Returns:
            List of strings representing build versions.
        """
        prefix = '%s-release/%s-' % (board, 'R%s' % milestone)
        builds = self._get_partial_object_path(prefix, '/')
        builds = [build[len(prefix):-1] for build in builds]
        builds.sort(key = lambda x: x)
        return builds
