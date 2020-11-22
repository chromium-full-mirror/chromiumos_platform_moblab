#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from moblab_common.utils import constants


class Constants(constants.Constants):
    """Class to maintain all reusable constant values within remote agent."""

    # The proto fields of NetworkStats
    BROKEN_CONNECTIONS = "broken_connections"
    DOWNLOAD_BITS_PER_SECOND = "download_bits_per_second"
    SERVER_ERRORS = "server_errors"
    UPLOAD_BITS_PER_SECOND = "upload_bits_per_second"

    # The proto fields of DiskStats
    FREE_DISK_SIZE_BYTES = "free_disk_size_bytes"
    TOTAL_DISK_SIZE_BYTES = "total_disk_size_bytes"

    # MoblabHost proto message grouped by attribute types
    DISK = "DISK"
    MOBLAB_BASIC = "MOBLAB_BASIC"
    NETWORK = "NETWORK"

    # MoblabDut proto message grouped by attribute types
    DUT_BASIC = "DUT_BASIC"
    DUT_STATUS = "DUT_STATUS"

    # Remote agent pubsub message types
    MOBLAB = "moblab"
    DUT = "dut"

    # Scheduler configuration file path
    SCHEDULER_CONFIG_PATH = (
        "/etc/moblab/remote_agent/services/scheduler/scheduler_config.yaml"
    )
