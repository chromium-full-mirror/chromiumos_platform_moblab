# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Boto file health checks for devserver."""


import netifaces
import os

from checkfiles.moblab import common

from moblab_common import host_connector


def GetIp():
    return host_connector.HostServicesConnector().get_ip()


class BotoFile(object):
    """Verifies that a Boto key exists."""

    def Check(self):
        """Verifies that moblab has a Boto for proper gs_offloader functioning.

        Returns:
            0 if a Boto key exists.
            -1 if a Boto key does not exist.
            -2 if the Boto key is empty.
        """
        if not os.path.exists(common.BOTO_PATH):
            return -1

        if 0 == os.stat(common.BOTO_PATH).st_size:
            return -2

        return 0

    def Diagnose(self, errcode):
        msg = "Boto key is %s. Please ensure your configuration is entered in the main UI"

        if -1 == errcode:
            return (msg % "missing", [])

        elif -2 == errcode:
            return (msg % "empty", [])

        return ("Unknown error reached with error code: %s" % errcode, [])
