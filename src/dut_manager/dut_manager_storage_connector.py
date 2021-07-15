# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple layer to abstract the grpc implementation from users."""


import logging
import grpc
import os

from lab import dut_manager_storage_pb2_grpc as grpc_stub
from lab import dut_manager_storage_pb2 as pb2
from lab.dut_manager_storage_pb2 import GetDutResponse
from lab.managed_dut_pb2 import ManagedDut


class DutManagerRpcError(Exception):
    pass


class DutManagerStorageRpcConnector(object):
    """Client for DutManagerStorage grpc service
    Abstracts out the grpc details of connecting
    to the moblab rpc configuration server.
    """

    channel = None
    stub = None

    @classmethod
    def connect(cls):
        """Connect to the grpc service, caching the connection.

        Raises:
            DutManagerRpcError: On a connection issue.
        """
        if not cls.channel or not cls.stub:
            address = os.getenv("DUT_MANAGER_STORAGE_GRPS_SERVICE_ADDRESS")
            cls.channel = grpc.insecure_channel(address)
            if cls.channel:
                cls.stub = grpc_stub.DutManagerStorageServiceStub(cls.channel)
                if not cls.stub:
                    raise DutManagerRpcError(
                        "Unable to connect to server %s" % address
                    )
            else:
                raise DutManagerRpcError("No server found %s" % address)

    @classmethod
    def disconnect(cls):
        """Invalidate the cached grpc server connection."""
        cls.channel = None
        cls.stub = None

    @classmethod
    def create_dut(cls):
        """ """
        cls.connect()
        try:
            request = pb2.CreateDutRequest()

            response = cls.stub.CreateDut(request)
            return response.dut if response else None
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            raise DutManagerRpcError("Error reading the %s dut")

    @classmethod
    def list_duts(cls):
        """Get the list of all DUTs managed by DUT Manager"""
        cls.connect()
        try:
            request = pb2.ListDutRequest()
            response = cls.stub.ListDut(request)
            return response.duts if response else None
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            raise DutManagerRpcError("Error listing duts")

    @classmethod
    def get_dut(cls, dut_ip: str) -> GetDutResponse:
        """Get managed dut details.

        Raises:
            MoblabRpcConnectorError: If rpc call failed.

        Returns: ManagedDut object
        """

        cls.connect()
        try:
            request = pb2.GetDutRequest(name=dut_ip)
            response = cls.stub.GetDut(request)
            return response.dut if response else None
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error reading the %s dut", dut_ip)
            raise DutManagerRpcError("Error reading the %s dut", dut_ip)

    # TODO Implement update endpoint
    @classmethod
    def update_dut(cls, managed_dut: ManagedDut, update_mask):
        """Update dut"""
        cls.connect()
        try:
            request = pb2.UpdateDutRequest(
                dut=managed_dut, update_mask=update_mask
            )
            response = cls.stub.UpdateDut(request)
            return response.dut if response else None
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            raise DutManagerRpcError("Error reading the %s dut")

    @classmethod
    def delete_dut(cls, dut_ip: str):
        """Delete the DUT from the storage

        Args:
            dut_ip: DUT's ip address

        Raises:
            MoblabRpcConnectorError: If rpc call fails.
        """
        cls.connect()
        try:
            request = pb2.DeleteDutRequest(name=dut_ip)
            cls.stub.DeleteDut(request)
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            raise DutManagerRpcError("Error reading the %s dut")
