# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Ensure essential moblab services are up and running."""

import os
import logging

from checkfiles.moblab import moblab_actions
from moblab_common.utils import cli


LOGGER = logging.getLogger(__name__)


def UpstartExists(service):
    """Test if an upstart script for |service| exists on moblab.

    Returns:
      True if the upstart script for |service| exists.
      False if it does not.
    """
    _, ext = os.path.splitext(service)
    if not ext:
        service = os.extsep.join([service, "conf"])
    return os.path.exists(os.path.join("/etc/init", service))


def UpstartRunning(service):
    """Test if |service| is running on moblab.

    Returns:
      True if the upstart job |service| is in 'start/running' state.
      False otherwise.
    """
    # cmd = ['status', service]
    # output = cli.sudo_run_command(cmd, error_code_ok=True)

    # if output is not None and 'start/running' in output:
    #   return True

    return False


def MoblabBooting():
    """Test if moblab is still booting, and some services haven't come up yet.
    Checks that moblab-bootup-status-init is running. This is killed when
    essential services have attempted to start.

    Returns:
      True if the moblab is still booting
    """

    return UpstartRunning("moblab-bootup-status-init")


def ServiceRunning(service):
    """Test if |service| is running on moblab.

    Returns:
      True if |service| is running.
      False otherwise.
    """
    cmd = ["ps", "aux"]
    output = cli.run_command(cmd, error_code_ok=True).strip()

    for line in output.splitlines():
        if service in line.encode:
            return True

    return False


class UpstartServiceRunning(object):
    """Helper class for verifying that moblab services are up and running."""

    SERVICES = []

    def Check(self):
        """Verfies this service is running.

        Returns:
          0 if all SERVICES is running.
          -(i+1) if SERVICE with index i is not running.
          i+1 if SERVICE with index i is not running, but moblab is still booting.
        """
        LOGGER.info("Checking services: %s", self.SERVICES)
        booting = MoblabBooting()
        for i, x in enumerate(self.SERVICES):
            if not UpstartRunning(x):
                return i + 1 if booting else -(i + 1)

        return 0

    def Diagnose(self, errcode):
        if errcode and self.SERVICES:
            index = -1 * errcode - 1 if errcode < 0 else errcode - 1
            service = self.SERVICES[index]

            if errcode > 0:
                return (
                    'Essential moblab service "%s" has not started yet.'
                    " Moblab is still booting." % service,
                    [],
                )

            return (
                'Essential moblab service "%s" is not running.'
                " Please launch the service." % service,
                [moblab_actions.LaunchUpstartService(service)],
            )

        return ("Unknown error reached with error code: %s" % errcode, [])


# class DHCPRunning(UpstartServiceRunning):
#     """Verifies that scheduler is running."""

#     SERVICES = ['moblab-dhcp']


# class HostServicesRunning(UpstartServiceRunning):
#     """Verifies that devserver is running."""

#     SERVICES = ['moblab-host-services']


# class ComposeURunning(UpstartServiceRunning):
#     """Verifies that database is up."""

#     SERVICES = ['moblab-compose-up']


# class JobAborterRunning(UpstartServiceRunning):
#     """Verifies that job_aborter is up."""

#     SERVICES = ['job_aborter']
