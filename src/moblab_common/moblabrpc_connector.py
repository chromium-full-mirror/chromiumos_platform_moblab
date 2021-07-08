# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple layer to abstrace the grpc implementation from users."""


import logging
import grpc

from moblab_common.proto import moblabrpc_pb2
from moblab_common.proto import moblabrpc_pb2_grpc

from google.protobuf import empty_pb2

DEFAULT_SERVER = "moblab-rpcserver:6002"

channel = None
stub = None


class MoblabRpcConnectorError(Exception):
    """Base class for all exceptions raised by this module."""

    pass


class MoblabRpcConnector(object):
    """Abstract out the grpc details of connecting the moblab rpc server.

    Raises:
        MoblabRpcConnectorError: On a connection issue.
    """

    channel = None
    stub = None

    @classmethod
    def connect(cls):
        """Connect to the grpc service, caching the connection.

        Raises:
            MoblabRpcConnectorError: On a connection issue.
        """
        if not cls.channel or not cls.stub:
            cls.channel = grpc.insecure_channel(DEFAULT_SERVER)
            if cls.channel:
                cls.stub = moblabrpc_pb2_grpc.MoblabRpcServiceStub(cls.channel)
                if not cls.stub:
                    raise MoblabRpcConnectorError(
                        "Unable to connect to server %s" % DEFAULT_SERVER
                    )
            else:
                raise MoblabRpcConnectorError(
                    "No server found %s" % DEFAULT_SERVER
                )

    @classmethod
    def disconnect(cls):
        """Invalidate the cached grpc server connection."""
        cls.channel = None
        cls.stub = None

    @classmethod
    def run_suite(
        cls, build_target, model, milestone, build_version, suite, pool=None
    ):
        """Run a suite test plan on a particular DUT/software combination.

        Args:
            build_target (string): The software build target e.g. hatch
            model (string): DUT hardware model, e.g. kukui
            milestone (string): Software milestone, e.g. 88
            build_version (string): Software version e.g. 12222.0.0
            suite (string): test suite plan, e.g. cts
            pool (string, optional): Named pool of DUT's to run the tests on.
                Defaults to None.

        Raises:
            MoblabRpcConnectorError: On a communication error.

        Returns:
            RunSuiteResponse:
                string message: Confirmation/error message.

        """
        # Call the host service to get a non volatile identifier.
        cls.connect()
        try:
            request = moblabrpc_pb2.RunSuiteRequest()
            request.suite = suite
            request.build_target = build_target
            request.milestone = milestone
            request.build_version = build_version
            request.model = model
            if pool:
                request.pool = pool
            response = cls.stub.run_suite(request)
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting the host identifier")
            raise MoblabRpcConnectorError("Error getting the host identifier")

    @classmethod
    def download_service_account(cls):
        """Copy the service account from the cloud bucket to local drive.

        Raises:
            MoblabRpcConnectorError: [description]
        """
        cls.connect()
        try:
            cls.stub.download_service_account(empty_pb2.Empty())
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting the service account.")
            raise MoblabRpcConnectorError("Error getting the service account.")

    @classmethod
    def get_jobs(cls, query_start, query_limit):
        """Returns the list of jobs with details

        Raises:
            MoblabRpcConnectorError: [description]
        """
        cls.connect()
        try:
            request = moblabrpc_pb2.GetJobsRequest()
            request.query_start = query_start
            request.query_limit = query_limit

            return cls.stub.get_jobs(request).jobs
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting jobs.")
            raise MoblabRpcConnectorError("Error getting getting jobs.")
