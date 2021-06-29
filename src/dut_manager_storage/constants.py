# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from lab.managed_dut_pb2 import ManagedDut

AFE_TO_DUT_STATUS_MAPPINGS = {
    "Verifying": ManagedDut.ManagedState.VERIFY,
    "Running": ManagedDut.ManagedState.LEASED,
    "Ready": ManagedDut.ManagedState.READY,
    "Repairing": ManagedDut.ManagedState.VERIFY,
    "Repair Failed": ManagedDut.ManagedState.FAILED,
    "Cleaning": ManagedDut.ManagedState.VERIFY,
    "Pending": ManagedDut.ManagedState.UNKNOWN,
    "Resetting": ManagedDut.ManagedState.RESET,
    "Provisioning": ManagedDut.ManagedState.PROVISION,
    "Unknown": ManagedDut.ManagedState.UNKNOWN,
    "Disconnected": ManagedDut.ManagedState.UNKNOWN,
    "Not Enrolled": ManagedDut.ManagedState.UNKNOWN,
    "": ManagedDut.ManagedState.UNKNOWN,
}

AFE_SPECIAL_TASK_TO_DUT_STATUS_MAPPINGS = {
    "Verify": ManagedDut.ManagedState.VERIFY,
    "Cleanup": ManagedDut.ManagedState.VERIFY,
    "Repair": ManagedDut.ManagedState.VERIFY,
    "Reset": ManagedDut.ManagedState.RESET,
    "Provision": ManagedDut.ManagedState.PROVISION,
    "": ManagedDut.ManagedState.UNKNOWN,
}
