# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import grpc
from google.protobuf.descriptor import Error

from lab.dut_manager_storage_pb2 import (
    CreateDutResponse,
    DeleteDutResponse,
    ListDutResponse,
    GetDutResponse,
    UpdateDutResponse,
)
from lab.dut_manager_storage_pb2_grpc import DutManagerStorageServiceServicer
from dut_manager_storage_service import (
    DutManagerStorageService,
    DutManagerStorageServicesException,
)

_LOGGER = logging.getLogger("dut-manager-storage")


class DutManagerStorageRpcService(DutManagerStorageServiceServicer):
    """Class that implements the DUT manager storage RPC servicer."""

    def __init__(self):
        """Initialize the storage service that interacts with the db."""
        super(DutManagerStorageRpcService, self).__init__()
        self.storage_service = DutManagerStorageService()

    def CreateDut(self, request, context):
        """Create an instance of managed DUT in the db."""
        self.storage_service.create_managed_dut(request.dut)
        return CreateDutResponse()

    def DeleteDut(self, request, context):
        """Delete the given instance of managed DUT from the db."""
        self.storage_service.delete_managed_dut(request.name)
        return DeleteDutResponse()

    def ListDut(self, request, context):
        """List all instances of managed DUT stored in the db."""
        try:
            managed_duts = self.storage_service.list_managed_duts()
        except DutManagerStorageServicesException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e)
            raise Error("Internal service error!")

        response = ListDutResponse(duts=managed_duts)
        _LOGGER.debug("ListDut response: %s", response)
        return response

    def GetDut(self, request, context):
        """Get the instance of given managed DUT from the db."""
        try:
            managed_dut = self.storage_service.get_managed_dut(request.name)
        except DutManagerStorageServicesException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e)
            raise Error("Internal service error!")

        response = GetDutResponse(dut=managed_dut)
        _LOGGER.debug("GetDut response: %s", response)
        return response

    def UpdateDut(self, request, context):
        """Update the given fields of a managed DUT in the db."""
        self.storage_service.update_dut(request.dut, request.update_mask)
        return UpdateDutResponse()
