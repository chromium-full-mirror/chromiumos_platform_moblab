# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Implementation of Inventory gRPC Service for Moblab."""

import logging
from chromiumos.test.lab.api.inventory_service_pb2_grpc import (
    InventoryServiceServicer,
)
from chromiumos.test.lab.api.inventory_service_pb2 import (
    GetDutTopologyResponse,
)
from chromiumos.test.lab.api.dut_pb2 import (
    DutTopology,
    Dut,
)

from chromiumos.test.lab.api.ip_endpoint_pb2 import (
    IpEndpoint,
)

_LOGGER = logging.getLogger("inventory")

INVALID_ARGUMENT_ERROR_MESSAGE = "Invalid Argument!"


class InventoryRpcService(InventoryServiceServicer):
    """Class that implements the lab inventory RPC servicer."""

    def __init__(self):
        """Initialize the inventory service."""
        super(InventoryRpcService, self).__init__()

    def GetDutTopology(self, request, context):
        """Get the DUT topology.

        This is no op for moblab so it will return empty proto.
        """
        if not request.id or not request.id.value:
            result = GetDutTopologyResponse.Failure(
                error_message=INVALID_ARGUMENT_ERROR_MESSAGE
            )
            resp = GetDutTopologyResponse(failure=result)
        else:
            dut_hostname = request.id.value
            dut = Dut(
                id=Dut.Id(value=dut_hostname),
                chromeos=Dut.ChromeOS(ssh=IpEndpoint(address=dut_hostname)),
            )
            dut_topology = DutTopology(id=request.id, duts=[dut])
            result = GetDutTopologyResponse.Success(dut_topology=dut_topology)
            resp = GetDutTopologyResponse(success=result)

        _LOGGER.debug("GetDutTopology response: %s", resp)
        yield resp
