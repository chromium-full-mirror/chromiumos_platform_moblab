# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the InventoryRpcService."""

import unittest
import grpc
import portpicker
from grpc.framework.foundation import logging_pool

from chromiumos.test.lab.api.inventory_service_pb2 import (
    GetDutTopologyRequest,
    GetDutTopologyResponse,
)
from chromiumos.test.lab.api.inventory_service_pb2_grpc import (
    InventoryServiceStub,
    add_InventoryServiceServicer_to_server,
)
from inventory_rpcservice import (
    InventoryRpcService,
    INVALID_ARGUMENT_ERROR_MESSAGE,
)
from chromiumos.test.lab.api.dut_pb2 import (
    DutTopology,
    Dut,
)

from chromiumos.test.lab.api.ip_endpoint_pb2 import (
    IpEndpoint,
)


class InventoryRpcServiceTest(unittest.TestCase):
    """Testing the InventoryRpcService code."""

    dut_hostname = "test_hostname"
    dut = Dut(
        id=Dut.Id(value=dut_hostname),
        chromeos=Dut.ChromeOS(ssh=IpEndpoint(address=dut_hostname)),
    )
    dut_topology_id = DutTopology.Id(value=dut_hostname)
    dut_topology = DutTopology(id=dut_topology_id, duts=[dut])
    success = GetDutTopologyResponse.Success(dut_topology=dut_topology)
    failure = GetDutTopologyResponse.Failure(
        error_message=INVALID_ARGUMENT_ERROR_MESSAGE
    )

    def setUp(self):
        """Initialize the inventory gRPC server."""
        super().setUp()
        port = portpicker.pick_unused_port()
        server_pool = logging_pool.pool(max_workers=25)
        self._server = grpc.server(server_pool)
        self._server.add_insecure_port(
            "[::]:{port}".format(port=port),
        )
        service = InventoryRpcService()
        add_InventoryServiceServicer_to_server(service, self._server)
        self._server.start()
        self._channel = grpc.insecure_channel(
            "localhost:{port}".format(port=port)
        )
        self._stub = InventoryServiceStub(self._channel)

    def tearDown(self):
        """Stop the inventory gRPC server."""
        self._channel.close()
        self._server.stop(None)
        return super().tearDown()

    def test_get_dut_topology(self):
        """Test GetDutTopology with valid request, expect success message."""
        request = GetDutTopologyRequest(id=self.dut_topology_id)

        # Response type is an iteratable grpc stream
        for response in self._stub.GetDutTopology(request):
            self.assertEqual(
                response, GetDutTopologyResponse(success=self.success)
            )

    def test_get_dut_topology_with_invalid_argument(self):
        """Test GetDutTopology with invalid request, expect failure message."""
        request = GetDutTopologyRequest(id=None)

        for response in self._stub.GetDutTopology(request):
            self.assertEqual(
                response, GetDutTopologyResponse(failure=self.failure)
            )


if __name__ == "__main__":
    unittest.main()
