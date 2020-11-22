# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Common lib for moblab checkfiles."""


#
# Boto file constants.
#
BOTO_PATH = "/home/moblab/.boto"
SERVICE_ACCOUNT_PATH = "/home/moblab/.service_account.json"
#
# disk_check constants.
#
# 100GB
DISK_SIZE_BYTES = 100 * 1024 * 1024 * 1024

MOBLAB_LABEL = "MOBLAB-STORAGE"

STATEFUL_MOUNTPOINT = "/"
MOBLAB_MOUNTPOINT = "/mnt/moblab"
MOBLAB_FILESYSTEM = "ext4"

DISK_FREE_THRESHOLD_PERCENT = 0.3
