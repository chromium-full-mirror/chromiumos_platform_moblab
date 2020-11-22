# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import sys
import os

from moblab_common import host_connector


def reboot():
    host_connector.HostServicesConnector().reboot()


def factory_reset():
    host_connector.HostServicesConnector.factory_reset()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        f = os.path.basename(sys.argv[1])
        locals()[f]()
