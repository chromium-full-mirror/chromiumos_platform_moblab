# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the DutManagerRpcService"""

import unittest
from unittest import mock
import grpc
import portpicker
from grpc.framework.foundation import logging_pool
from google.protobuf.field_mask_pb2 import FieldMask

from dut_manager_storage_connector import DutManagerRpcError
from dut_manager_rpcservice import DutManagerRpcService
from lab.managed_dut_pb2 import ManagedDut, NetworkIdentifier
from lab.managed_dut_pb2 import (
    ManagedDut,
    Pool,
    NetworkIdentifier,
    Lock,
)
from lab.dut_manager_pb2 import (
    GetManagedDutRequest,
    GetManagedDutResponse,
    ListManagedDutsRequest,
    ListManagedDutsResponse,
    UpdateManagedDutRequest,
    UpdateManagedDutResponse,
)
from chromiumos.test.api.dut_attribute_pb2 import (
    DutAttribute,
    DutAttributeList,
)
from lab.dut_manager_pb2_grpc import (
    add_DutManagerServiceServicer_to_server,
    DutManagerServiceStub,
)


class DutManagerRpcServiceTest(unittest.TestCase):
    """Testing the DutManagerRpcService code."""

    dut_name_1 = "test_ip_address_1"
    dut_name_2 = "test_ip_address_2"
    dut_identifier_1 = NetworkIdentifier(ip_address=dut_name_1)
    dut_identifier_2 = NetworkIdentifier(ip_address=dut_name_2)
    dut_attribute = DutAttribute(
        id=DutAttribute.Id(value="test_key"), field_path="test_value"
    )
    test_managed_dut_1 = ManagedDut(
        name=dut_identifier_1,
        display_name="test_display_name",
        tag=DutAttributeList(dut_attributes=[dut_attribute]),
        pool=[Pool(name="test_pool")],
        state=ManagedDut.ManagedState.READY,
        lock=Lock(reason="test_lock"),
        operator_notes="test_operator_notes",
        provisioned_firmware_version="test_provisioned_fw_version",
    )
    test_managed_dut_2 = ManagedDut(name=dut_identifier_2)
    update_field_mask = FieldMask(paths=["pool", "tag"])

    def setUp(self):
        super().setUp()
        port = portpicker.pick_unused_port()
        server_pool = logging_pool.pool(max_workers=25)
        self._server = grpc.server(server_pool)
        self._server.add_insecure_port(
            "[::]:{port}".format(port=port),
        )
        service = DutManagerRpcService()
        add_DutManagerServiceServicer_to_server(service, self._server)
        self._server.start()
        self._channel = grpc.insecure_channel(
            "localhost:{port}".format(port=port)
        )
        self._stub = DutManagerServiceStub(self._channel)

    def tearDown(self):
        self._channel.close()
        self._server.stop(None)
        return super().tearDown()

    @mock.patch(
        "dut_manager_storage_connector.DutManagerStorageRpcConnector.get_dut"
    )
    def test_get_managed_dut(self, mock_get_dut):
        request = GetManagedDutRequest(name=self.dut_identifier_1)
        mock_get_dut.return_value = self.test_managed_dut_1

        response = self._stub.GetManagedDut(request)

        mock_get_dut.assert_called_once_with(self.dut_name_1)
        self.assertEqual(
            response, GetManagedDutResponse(dut=self.test_managed_dut_1)
        )

    @mock.patch(
        "dut_manager_storage_connector.DutManagerStorageRpcConnector.get_dut"
    )
    def test_get_managed_dut_with_internal_failure(self, mock_get_dut):
        request = GetManagedDutRequest(name=self.dut_identifier_1)
        mock_get_dut.side_effect = DutManagerRpcError()

        with self.assertRaises(grpc.RpcError) as exception_context:
            self._stub.GetManagedDut(request)

        mock_get_dut.assert_called_once()
        self.assertIs(
            exception_context.exception.code(),
            grpc.StatusCode.INTERNAL,
        )

    @mock.patch(
        "dut_manager_storage_connector.DutManagerStorageRpcConnector.get_dut"
    )
    def test_get_managed_dut_with_invalid_argument(self, mock_get_dut):
        request = GetManagedDutRequest(name=None)

        with self.assertRaises(grpc.RpcError) as exception_context:
            self._stub.GetManagedDut(request)

        mock_get_dut.assert_not_called()
        self.assertIs(
            exception_context.exception.code(),
            grpc.StatusCode.INVALID_ARGUMENT,
        )

    @mock.patch(
        "dut_manager_storage_connector.DutManagerStorageRpcConnector.list_duts"
    )
    def test_list_managed_duts(self, mock_list_duts):
        request = ListManagedDutsRequest()
        duts = [self.test_managed_dut_1, self.test_managed_dut_2]
        mock_list_duts.return_value = duts

        response = self._stub.ListManagedDuts(request)

        mock_list_duts.assert_called_once()
        self.assertEqual(response, ListManagedDutsResponse(duts=duts))

    @mock.patch(
        "dut_manager_storage_connector.DutManagerStorageRpcConnector.list_duts"
    )
    def test_list_managed_duts_with_internal_failure(self, mock_list_duts):
        request = ListManagedDutsRequest()
        mock_list_duts.side_effect = DutManagerRpcError()

        with self.assertRaises(grpc.RpcError) as exception_context:
            self._stub.ListManagedDuts(request)

        mock_list_duts.assert_called_once()
        self.assertIs(
            exception_context.exception.code(),
            grpc.StatusCode.INTERNAL,
        )

    @mock.patch(
        "dut_manager_storage_connector.DutManagerStorageRpcConnector.update_dut"
    )
    def test_update_managed_dut(self, mock_update_dut):
        request = UpdateManagedDutRequest(
            dut=self.test_managed_dut_1, update_mask=self.update_field_mask
        )

        response = self._stub.UpdateManagedDut(request)

        mock_update_dut.assert_called_once_with(
            self.test_managed_dut_1, self.update_field_mask
        )
        self.assertEqual(response, UpdateManagedDutResponse())

    @mock.patch(
        "dut_manager_storage_connector.DutManagerStorageRpcConnector.update_dut"
    )
    def test_update_managed_dut_with_internal_failure(self, mock_update_dut):
        request = UpdateManagedDutRequest(
            dut=self.test_managed_dut_1, update_mask=self.update_field_mask
        )
        mock_update_dut.side_effect = DutManagerRpcError()

        with self.assertRaises(grpc.RpcError) as exception_context:
            self._stub.UpdateManagedDut(request)

        mock_update_dut.assert_called_once_with(
            self.test_managed_dut_1, self.update_field_mask
        )
        self.assertIs(
            exception_context.exception.code(),
            grpc.StatusCode.INTERNAL,
        )


if __name__ == "__main__":
    unittest.main()
