from google.protobuf.descriptor import Error
import grpc

from lab import dut_manager_pb2
from lab import dut_manager_pb2_grpc

from dut_manager_storage_connector import (
    DutManagerRpcError,
    DutManagerStorageRpcConnector,
)

import logging

_LOGGER = logging.getLogger("dut-manager")


class DutManagerRpcService(dut_manager_pb2_grpc.DutManagerServiceServicer):
    """Grpc layer for the Dut Manager service implementation"""

    def __init__(self):
        super(DutManagerRpcService, self).__init__()

    def ListManagedDuts(self, request, context):
        """List all managed DUTs."""
        try:
            duts = DutManagerStorageRpcConnector.list_duts()
            resp = dut_manager_pb2.ListManagedDutsResponse(
                duts=duts,
            )
            _LOGGER.debug("ListManagedDuts response: %s", resp)
            return resp
        except DutManagerRpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e)
            _LOGGER.exception("ListManagedDuts handler failed")
            raise

    def GetManagedDut(self, request, context):
        """Get the DUT details including state history for a given DUT."""
        if not request.name or not request.name.ip_address:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Please provide a valid DUT's IP address")
            raise Error("Invalid argument!")

        try:
            dut = DutManagerStorageRpcConnector.get_dut(
                request.name.ip_address
            )
            resp = dut_manager_pb2.GetManagedDutResponse(
                dut=dut,
            )
            _LOGGER.debug("GetManagedDut response: %s", resp)
            return resp
        except DutManagerRpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e)
            _LOGGER.exception("GetManagedDut handler failed")
            raise

    def UpdateManagedDut(self, request, context):
        """Update managed DUT given by DUT name."""
        try:
            DutManagerStorageRpcConnector.update_dut(
                request.dut, request.update_mask
            )
            _LOGGER.debug("UpdateManagedDut request: %s", request)
            return dut_manager_pb2.UpdateManagedDutResponse()
        except DutManagerRpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e)
            _LOGGER.exception("UpdateManagedDut handler failed")
            raise
