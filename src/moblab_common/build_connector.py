# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""

import logging

# pylint: disable=no-name-in-module, import-error
from google.cloud.storage import Client as GcsClient
from moblab_common.moblab_build_connector import exception_handler

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
            raise MoblabBuildConnectorException("Missing bucket name")
        self.moblab_bucket_name = moblab_bucket_name
        if storage_client:
            self.storage_client = storage_client
        else:
            try:
                self.storage_client = GcsClient()
            except auth_exceptions.DefaultCredentialsError as e:
                logging.info("No credentials loaded")
                raise MoblabBuildConnectorException("Invalid Credentials")

    @exception_handler(unhandled_exception_message="Encountered API error when getting partial object path.")
    def _get_partial_object_path(self, prefix, delimiter):
        blob_itr = self.storage_client.bucket(
            self.moblab_bucket_name
        ).list_blobs(prefix=prefix, delimiter=delimiter)
        # pylint: disable=pointless-statement
        [None for _ in blob_itr]
        return [partial_path for partial_path in blob_itr.prefixes]

    def get_boards_available(self):
        """Lists the available boards, aka build targets, in the partner bucket.

        Returns:
            List of strings representing boards.
        """
        possible_boards = self._get_partial_object_path(None, "/")
        possible_boards = [
            board for board in possible_boards if board.endswith("-release/")
        ]
        available_boards = [
            board[: -len("-release/")] for board in possible_boards
        ]
        available_boards.sort(key=lambda x: x)
        return available_boards

    def get_milestones_available(self, board):
        """Lists the available milestones in the partner bucket.

        Args:
            board (str): Build target name.
        Returns:
            List of strings representing build versions.
        """
        prefix = "%s-release/R" % board
        milestones = self._get_partial_object_path(prefix, "-")
        milestones = [milestone[len(prefix) : -1] for milestone in milestones]
        milestones.sort(key=lambda x: x)
        return milestones

    def get_builds_for_milestone(self, board, milestone):
        """Lists the available build versions in the partner bucket.

        Args:
            board (str): Build target name.
            milestone (str): The milestone number.
        Returns:
            List of strings representing build versions.
        """
        prefix = "%s-release/%s-" % (board, "R%s" % milestone)
        builds = self._get_partial_object_path(prefix, "/")
        builds = [build[len(prefix) : -1] for build in builds]
        builds.sort(key=lambda x: x)
        # local builds are advised to be kept in separate folder
        # {board}-local/*
        local_prefix = "%s-local/%s-" % (board, "R%s" % milestone)
        local_builds = self._get_partial_object_path(local_prefix, "/")
        local_builds = [
            local_build[len(local_prefix) : -1] for local_build in local_builds
        ]
        return builds + local_builds

    @exception_handler(unhandled_exception_message="Encountered API error when checking moblab bucket is in asia.")
    def is_moblab_bucket_in_asia(self, bucket_name: str) -> bool:
        """Check the bucket is in Asia.
        Args:
            bucket_name(str): Bucket name.
        Returns:
            Boolean
        """
        if not bucket_name:
            raise ArgumentException("Missing the bucket name")
        bucket = GcsClient().bucket(bucket_name)
        bucket.reload()
        return "asia" in bucket.location.lower()
