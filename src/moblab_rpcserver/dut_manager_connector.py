# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple layer to abstract the grpc implementation from users."""


import logging
import grpc
import os

from lab import dut_manager_pb2
from lab import dut_manager_pb2_grpc as grpc_stub
from moblab_common.moblabrpc_connector import MoblabRpcConnectorError


class DutManagerRpcConnector(object):
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
            address = os.getenv("DUT_MANAGER_GRPS_SERVICE_ADDRESS")
            cls.channel = grpc.insecure_channel(address)
            if cls.channel:
                cls.stub = grpc_stub.DutManagerServiceStub(cls.channel)
                if not cls.stub:
                    raise MoblabRpcConnectorError(
                        "Unable to connect to server %s" % address
                    )
            else:
                raise MoblabRpcConnectorError("No server found %s" % address)

    @classmethod
    def disconnect(cls):
        """Invalidate the cached grpc server connection."""
        cls.channel = None
        cls.stub = None

    @classmethod
    def list_managed_duts(cls):
        """List all DUTs managed by DUT Manager.

        Raises:
            MoblabRpcConnectorError: If rpc call failed.

        Returns: LIst of ManagedDut objects.
        """

        cls.connect()
        try:
            request = dut_manager_pb2.ListManagedDutsRequest()
            response = cls.stub.ListManagedDuts(request)
            return response.duts if response else None
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error listing all duts")
            raise MoblabRpcConnectorError("Error listing all duts")

    @classmethod
    def get_managed_dut(cls, dut_ip):
        """Get managed dut details.

        Raises:
            MoblabRpcConnectorError: If rpc call failed.

        Returns: ManagedDut object
        """

        cls.connect()
        try:
            request = dut_manager_pb2.GetManagedDutRequest()
            request.name.ip_address = dut_ip
            response = cls.stub.GetManagedDut(request)
            return response.dut if response else None
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error reading the %s dut", dut_ip)
            raise MoblabRpcConnectorError("Error reading the %s dut", dut_ip)
