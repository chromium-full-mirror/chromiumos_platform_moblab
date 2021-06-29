from google.protobuf.descriptor import Error
import grpc

from lab import dut_manager_pb2
from lab import dut_manager_pb2_grpc
from lab import managed_dut_pb2

import logging

_LOGGER = logging.getLogger("dut-manager")


class DutManagerRpcService(dut_manager_pb2_grpc.DutManagerServiceServicer):
    """Grpc layer for the Dut Manager service implementation"""

    def GetManagedDut(self, request, context):
        """Get the DUT details including state history for a given Dut."""
        if not request.name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Please provide a valid DUT's IP address")
            raise Error("Invalid argument!")

        resp = dut_manager_pb2.GetManagedDutResponse(
            dut=managed_dut_pb2.ManagedDut(
                display_name=request.name.ip_address,
            ),
        )
        _LOGGER.debug("GetManagedDut response: %s", resp)
        return resp
