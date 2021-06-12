# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Boto file health checks for devserver."""

import os

from checkfiles.moblab import common
from checkfiles.moblab import moblab_actions
from moblab_common import host_connector
from checkfiles.moblab import boto_check


def GetIp():
    return host_connector.HostServicesConnector().get_ip()


class ServiceAccountFile(object):
    """Verifies that a Service Account key exists."""

    def Check(self):
        """Verify that moblab has a service account for cloud API calls.
        Bypass the test if boto file check fails.

        Returns:
          0 if a service account key exists.
          -1 if a service account key does not exist.
          -2 if the service account key is empty.
        """
        boto_file_check = boto_check.BotoFile()
        if boto_file_check.Check() != 0:
            return 0

        if not os.path.exists(common.SERVICE_ACCOUNT_PATH):
            return -1

        if 0 == os.stat(common.SERVICE_ACCOUNT_PATH).st_size:
            return -2

        return 0

    def Diagnose(self, errcode):
        msg = "Service account is %s.  Please download a new version."

        if -1 == errcode:
            return (
                msg % "missing",
                [moblab_actions.DownloadServiceAccount()],
            )

        elif -2 == errcode:
            return (msg % "empty", [moblab_actions.DownloadServiceAccount()])

            return ("Unknown error reached with error code: %s" % errcode, [])
