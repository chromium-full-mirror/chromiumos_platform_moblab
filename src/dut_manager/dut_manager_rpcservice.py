# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import concurrent
from google.protobuf.descriptor import Error
import grpc

from lab import dut_manager_pb2
from lab import dut_manager_pb2_grpc
from google.protobuf import any_pb2

from chromiumos.longrunning import operations_pb2
from chromiumos.longrunning import operations_pb2_grpc

from dut_manager_storage_connector import (
    DutManagerRpcError,
    DutManagerStorageRpcConnector,
)

import logging

_LOGGER = logging.getLogger("dut-manager")


class DutManagerRpcService(dut_manager_pb2_grpc.DutManagerServiceServicer):
    """Grpc layer for the Dut Manager service implementation"""

    def __init__(self, operations_service):
        super(DutManagerRpcService, self).__init__()
        self.operations_service = operations_service

    def CreateManagedDut(self, request, context):
        """Create and add a DUT to managed DUTs collection."""
        try:
            _LOGGER.info("CreateManagedDut received request: %s", request)
            ip = request.name.ip_address
            operation_name = "create_%s" % ip

            def enroll_func():
                try:
                    DutManagerStorageRpcConnector.create_dut(ip)
                    _LOGGER.debug("enroll_func is completed")
                except Exception:
                    _LOGGER.exception("enroll_func unhandled exception")
                    raise

            self.operations_service.AddRunningOperation(
                operation_name, enroll_func
            )
            return operations_pb2.Operation(name=operation_name, done=False)
        except DutManagerRpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e)
            _LOGGER.exception("CreateManagedDut handler failed")
            raise
        except Exception:
            _LOGGER.exception("CreateManagedDut unhandled exception")
            raise

    def ListManagedDuts(self, request, context):
        """List all managed DUTs."""
        try:
            duts = DutManagerStorageRpcConnector.list_duts()
            resp = dut_manager_pb2.ListManagedDutsResponse(
                duts=duts,
            )
            _LOGGER.debug("ListManagedDuts response complete")
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

    def DeleteManagedDut(self, request, context):
        """Delete DUT from the managed DUTs collection."""
        try:
            DutManagerStorageRpcConnector.delete_dut(request.name.ip_address)
            _LOGGER.debug("DeleteManagedDut request: %s", request)
            return dut_manager_pb2.UpdateManagedDutResponse()
        except DutManagerRpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e)
            _LOGGER.exception("DeleteManagedDut handler failed")
            raise


class DutManagerOperationsRpcService(operations_pb2_grpc.OperationsServicer):
    """Grpc layer for the Dut Manager service implementation"""

    def __init__(self):
        super(DutManagerOperationsRpcService, self).__init__()
        self.running_opearions_list = {}
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=20
        )

    def AddRunningOperation(self, name, func):
        if (
            name in self.running_opearions_list
            and not self.running_opearions_list[name].done()
        ):
            return

        future = self._thread_pool.submit(func)
        self.running_opearions_list[name] = future

    def GetOperation(self, request, context):
        if request.name in self.running_opearions_list:
            task = self.running_opearions_list[request.name]
            _LOGGER.debug("operation status: %s - %s", request.name, task)

            if task.done() and task.exception():
                return operations_pb2.Operation(
                    name=request.name,
                    done=True,
                    error=grpc.Status(
                        code=grpc.StatusCode.INTERNAL,
                        details=task.exception(),
                    ),
                )
            if task.done() and task.cancelled():
                return operations_pb2.Operation(
                    name=request.name,
                    done=True,
                    error=grpc.Status(
                        code=grpc.StatusCode.CANCELLED,
                        details="Operation was cancelled",
                    ),
                )
            if task.done():
                any_response = any_pb2.Any()
                any_response.Pack(dut_manager_pb2.CreateManagedDutResponse())
                return operations_pb2.Operation(
                    name=request.name,
                    done=True,
                    response=any_response,
                )
            return operations_pb2.Operation(name=request.name, done=False)

        else:
            _LOGGER.debug(
                "self.running_opearions_list: %s", self.running_opearions_list
            )

            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Operation not found")
            raise DutManagerRpcError("Operation not found", request.name)
