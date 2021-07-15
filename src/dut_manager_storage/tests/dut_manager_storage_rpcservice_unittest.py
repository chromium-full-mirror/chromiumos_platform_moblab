# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the DutManagerStorageRpcService"""

import unittest
from unittest import mock
import grpc
import portpicker
from grpc.framework.foundation import logging_pool
from google.protobuf.field_mask_pb2 import FieldMask
from dut_manager_storage_rpcservice import (
    DutManagerStorageRpcService,
)
from lab.dut_manager_storage_pb2_grpc import (
    add_DutManagerStorageServiceServicer_to_server,
    DutManagerStorageServiceStub,
)
from dut_manager_storage_service import DutManagerStorageServicesException
from lab.dut_manager_storage_pb2 import (
    CreateDutRequest,
    CreateDutResponse,
    DeleteDutRequest,
    DeleteDutResponse,
    GetDutRequest,
    GetDutResponse,
    ListDutRequest,
    ListDutResponse,
    UpdateDutRequest,
    UpdateDutResponse,
)
from lab.managed_dut_pb2 import ManagedDut, NetworkIdentifier


class DutManagerStorageRpcServiceTest(unittest.TestCase):
    """Testing the DutManagerStorageRpcService code."""

    dut_name_1 = "test_ip_1"
    dut_name_2 = "test_ip_2"
    dut_1 = ManagedDut(name=NetworkIdentifier(ip_address=dut_name_1))
    dut_2 = ManagedDut(name=NetworkIdentifier(ip_address=dut_name_2))
    field_mask = FieldMask(paths=["pool"])

    def setUp(self):
        super().setUp()
        port = portpicker.pick_unused_port()
        server_pool = logging_pool.pool(max_workers=25)
        self._server = grpc.server(server_pool)
        self._server.add_insecure_port(
            "[::]:{port}".format(port=port),
        )
        service = DutManagerStorageRpcService()
        add_DutManagerStorageServiceServicer_to_server(service, self._server)
        self._server.start()
        self._channel = grpc.insecure_channel(
            "localhost:{port}".format(port=port)
        )
        self._stub = DutManagerStorageServiceStub(self._channel)

    def tearDown(self):
        self._channel.close()
        self._server.stop(None)
        return super().tearDown()

    @mock.patch(
        "dut_manager_storage_service.DutManagerStorageService.create_managed_dut"
    )
    def test_create_dut(self, mock_create_managed_dut):
        request = CreateDutRequest(dut=self.dut_1)

        response = self._stub.CreateDut(request)

        mock_create_managed_dut.assert_called_once()
        self.assertEqual(response, CreateDutResponse())

    @mock.patch(
        "dut_manager_storage_service.DutManagerStorageService.delete_managed_dut"
    )
    def test_delete_dut(self, mock_delete_managed_dut):
        request = DeleteDutRequest(name=self.dut_name_1)
        response = self._stub.DeleteDut(request)

        mock_delete_managed_dut.assert_called_once_with(self.dut_name_1)
        self.assertEqual(response, DeleteDutResponse())

    @mock.patch(
        "dut_manager_storage_service.DutManagerStorageService.get_managed_dut"
    )
    def test_get_dut(self, mock_get_managed_dut):
        request = GetDutRequest(name=self.dut_name_1)
        mock_get_managed_dut.return_value = self.dut_1

        response = self._stub.GetDut(request)

        mock_get_managed_dut.assert_called_once_with(self.dut_name_1)
        self.assertEqual(response, GetDutResponse(dut=self.dut_1))

    @mock.patch(
        "dut_manager_storage_service.DutManagerStorageService.get_managed_dut"
    )
    def test_get_dut_with_failure(self, mock_get_managed_dut):
        request = GetDutRequest(name=self.dut_name_1)
        mock_get_managed_dut.side_effect = DutManagerStorageServicesException()

        with self.assertRaises(grpc.RpcError) as exception_context:
            self._stub.GetDut(request)

        mock_get_managed_dut.assert_called_once()
        self.assertIs(
            exception_context.exception.code(),
            grpc.StatusCode.INTERNAL,
        )

    @mock.patch(
        "dut_manager_storage_service.DutManagerStorageService.list_managed_duts"
    )
    def test_list_dut(self, mock_list_managed_duts):
        request = ListDutRequest()
        duts = [self.dut_1, self.dut_2]
        mock_list_managed_duts.return_value = duts

        response = self._stub.ListDut(request)

        mock_list_managed_duts.assert_called_once()
        self.assertEqual(response, ListDutResponse(duts=duts))

    @mock.patch(
        "dut_manager_storage_service.DutManagerStorageService.list_managed_duts"
    )
    def test_list_dut_with_failure(self, mock_list_managed_duts):
        request = ListDutRequest()
        mock_list_managed_duts.side_effect = (
            DutManagerStorageServicesException()
        )

        with self.assertRaises(grpc.RpcError) as exception_context:
            self._stub.ListDut(request)

        mock_list_managed_duts.assert_called_once()
        self.assertIs(
            exception_context.exception.code(),
            grpc.StatusCode.INTERNAL,
        )

    @mock.patch(
        "dut_manager_storage_service.DutManagerStorageService.update_managed_dut"
    )
    def test_update_dut(self, mock_update_managed_dut):
        request = UpdateDutRequest(dut=self.dut_1, update_mask=self.field_mask)

        response = self._stub.UpdateDut(request)

        mock_update_managed_dut.assert_called_once_with(
            self.dut_1, self.field_mask
        )
        self.assertEqual(response, UpdateDutResponse())

    @mock.patch(
        "dut_manager_storage_service.DutManagerStorageService.update_managed_dut"
    )
    def test_update_dut_with_failure(self, mock_update_managed_dut):
        request = UpdateDutRequest(dut=self.dut_1, update_mask=self.field_mask)
        mock_update_managed_dut.side_effect = (
            DutManagerStorageServicesException()
        )

        with self.assertRaises(grpc.RpcError) as exception_context:
            self._stub.UpdateDut(request)

        mock_update_managed_dut.assert_called_once_with(
            self.dut_1, self.field_mask
        )
        self.assertIs(
            exception_context.exception.code(),
            grpc.StatusCode.INTERNAL,
        )


if __name__ == "__main__":
    unittest.main()
