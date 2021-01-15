# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple layer to abstract the grpc implementation from users."""


import logging
import grpc

from moblab_common.proto import moblab_configuration_rpc_pb2
from moblab_common.proto import moblab_configuration_rpc_pb2_grpc as grpc_stub

from moblab_common.moblabrpc_connector import MoblabRpcConnectorError

from google.protobuf import empty_pb2

DEFAULT_SERVER = "moblab-rpcserver:6002"

channel = None
stub = None


class MoblabConfigurationRpcConnector(object):
    """Abstract out the grpc details of connecting the moblab rpc
    configuration server.
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
                cls.stub = grpc_stub.MoblabConfigurationServiceStub(
                    cls.channel
                )
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
    def get_stable_build_version(cls):
        """Read stable build version configuration.

        Raises:
            MoblabRpcConnectorError: If rpc call failed.

        Returns: StableVersion
        """
        cls.connect()
        try:
            request = (
                moblab_configuration_rpc_pb2.GetStableBuildVersionRequest()
            )
            response = cls.stub.get_stable_build_version(request)
            return response.stable_version if response else None
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting the host identifier")
            raise MoblabRpcConnectorError("Error getting the host identifier")

    @classmethod
    def get_stable_build_version_resolved(cls):
        """Read stable build version resolved between default and override.

        Raises:
            MoblabRpcConnectorError: If rpc call fails.

        Returns:
            Configured Build Version string
        """
        response = cls.get_stable_build_version()
        if response.override_version:
            return response.override_version
        return response.default_version
