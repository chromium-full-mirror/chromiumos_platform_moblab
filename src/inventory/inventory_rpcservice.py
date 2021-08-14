# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging

from chromiumos.test.lab.api.inventory_service_pb2_grpc import (
    InventoryServiceServicer,
)

_LOGGER = logging.getLogger("inventory")


class InventoryRpcService(InventoryServiceServicer):
    """Class that implements the lab inventory RPC servicer."""

    def __init__(self):
        """Initialize the inventory service."""
        super(InventoryRpcService, self).__init__()

    def GetDutTopology(self, request, context):
        """Get the DUT topology."""
        pass
