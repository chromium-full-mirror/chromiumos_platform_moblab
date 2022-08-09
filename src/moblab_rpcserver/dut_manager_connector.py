# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple layer to abstract the grpc implementation from users."""


import asyncio
import logging
import grpc
import os

from lab import managed_dut_pb2
from lab import dut_manager_pb2
from lab import dut_manager_pb2_grpc as grpc_stub
from chromiumos.longrunning import operations_pb2
from chromiumos.longrunning import operations_pb2_grpc

from moblab_common import moblabrpc_connector


class DutManagerRpcConnectorAsync(object):
    """Abstract out the grpc details of connecting the moblab rpc
    configuration server.
    """

    channel = None
    stub = None
    operations_stub = None

    @classmethod
    def connect(cls):
        """Connect to the grpc service, caching the connection.

        Raises:
            MoblabRpcConnectorError: On a connection issue.
        """
        if not cls.channel or not cls.stub:
            address = os.getenv("DUT_MANAGER_GRPS_SERVICE_ADDRESS")
            cls.channel = grpc.aio.insecure_channel(address)
            if cls.channel:
                cls.stub = grpc_stub.DutManagerServiceStub(cls.channel)
                if not cls.stub:
                    raise moblabrpc_connector.MoblabRpcConnectorError(
                        "Unable to connect to DutManager service at %s"
                        % address
                    )
                cls.operations_stub = operations_pb2_grpc.OperationsStub(
                    cls.channel
                )
                if not cls.operations_stub:
                    raise moblabrpc_connector.MoblabRpcConnectorError(
                        "Unable to connect to Operations service at %s"
                        % address
                    )
            else:
                raise moblabrpc_connector.MoblabRpcConnectorError(
                    "No server found %s" % address
                )

    @classmethod
    def disconnect(cls):
        """Invalidate the cached grpc server connection."""
        cls.channel = None
        cls.stub = None
        cls.operations_stub = None

    @classmethod
    async def create_managed_dut(cls, ip):
        """Create and add managed DUT to the list of managed DUTs.

        Raises:
            MoblabRpcConnectorError: If rpc call failed.
        """
        cls.connect()
        try:
            request = dut_manager_pb2.CreateManagedDutRequest(
                name=managed_dut_pb2.NetworkIdentifier(ip_address=ip),
                display_name=ip,
            )
            operation = await cls.stub.CreateManagedDut(request)
            logging.debug("Operation returned: %s", operation)
            operation_request = operations_pb2.GetOperationRequest(
                name=operation.name
            )
            while not operation.done:
                operation = await cls.operations_stub.GetOperation(
                    operation_request
                )
                logging.debug("tick: Operation returned: %s", operation)
                await asyncio.sleep(1)
            return operation.response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error enrolling dut %s", ip)
            raise moblabrpc_connector.MoblabRpcConnectorError(
                "Error enrolling dut %s" % ip
            )

    @classmethod
    async def list_managed_duts(cls):
        """List all DUTs managed by DUT Manager.

        Raises:
            MoblabRpcConnectorError: If rpc call failed.

        Returns: List of ManagedDut objects.
        """

        cls.connect()
        try:
            request = dut_manager_pb2.ListManagedDutsRequest()
            response = await cls.stub.ListManagedDuts(request)
            return response.duts if response else None
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error listing all duts")
            raise moblabrpc_connector.MoblabRpcConnectorError(
                "Error listing all duts"
            )


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
                    raise moblabrpc_connector.MoblabRpcConnectorError(
                        "Unable to connect to DutManager service at %s"
                        % address
                    )
            else:
                raise moblabrpc_connector.MoblabRpcConnectorError(
                    "No server found %s" % address
                )

    @classmethod
    def disconnect(cls):
        """Invalidate the cached grpc server connection."""
        cls.channel = None
        cls.stub = None

    @classmethod
    def get_managed_dut(cls, dut_ip: str):
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
            raise moblabrpc_connector.MoblabRpcConnectorError(
                "Error reading the %s dut", dut_ip
            )

    @classmethod
    def update_managed_dut(cls, dut, field_mask):
        """Update managed dut details.

        Raises:
            MoblabRpcConnectorError: If rpc call failed.

        Returns: None
        """

        cls.connect()
        try:
            request = dut_manager_pb2.UpdateManagedDutRequest(
                dut=dut, update_mask=field_mask
            )
            cls.stub.UpdateManagedDut(request)
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            error_msg = "Error updating dut: {}".format(dut.name.ip_address)
            logging.exception(error_msg)
            raise moblabrpc_connector.MoblabRpcConnectorError(error_msg)

    @classmethod
    def delete_managed_dut(cls, dut_ip: str):
        """Delete dut from managed dut collection.

        Raises:
            MoblabRpcConnectorError: If rpc call failed.

        Returns: None
        """

        cls.connect()
        try:
            request = dut_manager_pb2.DeleteManagedDutRequest(
                name=managed_dut_pb2.NetworkIdentifier(ip_address=dut_ip)
            )
            cls.stub.DeleteManagedDut(request)
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            error_msg = "Error deleting dut: {}".format(dut_ip)
            logging.exception(error_msg)
            raise moblabrpc_connector.MoblabRpcConnectorError(error_msg)
