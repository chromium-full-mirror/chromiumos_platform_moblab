# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from lab.dut_manager_storage_pb2 import (
    CreateDutResponse,
    DeleteDutResponse,
    ListDutResponse,
    GetDutResponse,
    UpdateDutResponse,
)
from lab.dut_manager_storage_pb2_grpc import DutManagerStorageServiceServicer
from dut_manager_storage_service import DutManagerStorageService


class DutManagerStorageRpcService(DutManagerStorageServiceServicer):
    """Class that implements the DUT manager storage RPC servicer."""

    def __init__(self):
        """Initialize the storage service that interacts with the db."""
        super(DutManagerStorageRpcService, self).__init__()
        self.storage_service = DutManagerStorageService()

    def CreateDut(self, request, context):
        """Create an instance of managed DUT in the db."""
        self.storage_service.CreateDut(request.dut)
        return CreateDutResponse()

    def DeleteDut(self, request, context):
        """Delete the given instance of managed DUT from the db."""
        self.storage_service.DeleteDut(request.name)
        return DeleteDutResponse()

    def ListDut(self, request, context):
        """List all instances of managed DUT stored in the db."""
        managed_duts = self.storage_service.ListDut()
        return ListDutResponse(duts=managed_duts)

    def GetDut(self, request, context):
        """Get the instance of given managed DUT from the db."""
        managed_dut = self.storage_service.GetDut(request.name)
        return GetDutResponse(dut=managed_dut)

    def UpdateDut(self, request, context):
        """Update the given fields of a managed DUT in the db."""
        self.storage_service.UpdateDut(request.dut, request.update_mask)
        return UpdateDutResponse()
