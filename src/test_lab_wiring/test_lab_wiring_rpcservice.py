# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import grpc

from chromiumos.config.api.test.tls.wiring_pb2_grpc import WiringServicer


_LOGGER = logging.getLogger("dut-manager-storage")


class TestLabWiringRpcService(WiringServicer):
    """Class that implements the DUT manager storage RPC servicer."""

    def GetDut(self, request, context):
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def SetDutPowerSupply(self, request, context):
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def CacheForDut(self, request, context):
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def CallServo(self, request, context):
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def ExposePortToDut(self, request, context):
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError
