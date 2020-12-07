# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Ensure essential moblab services are up and running."""

import docker
import logging

from checkfiles.moblab import moblab_actions
from moblab_common.utils import cli


LOGGER = logging.getLogger(__name__)


def ContainerRunning(service):
    """Test if |service| is running on moblab.

    Returns:
      True if |service| is running.
      False otherwise.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(service)
        return container.status == "running"

    except (docker.errors.NotFound, docker.errors.APIError):
        return False
    return True


class DockerContainerRunning(object):
    """Helper class for verifying that moblab services are up and running."""

    SERVICES = {}

    def Check(self):
        """Verfies this service is running.

        Returns:
          0 if all SERVICES is running.
          -(i+1) if SERVICE with index i is not running.
          i+1 if SERVICE with index i is not running, but moblab is still
            booting.
        """
        LOGGER.info("Checking docker containers: %s", self.SERVICES.keys())
        for i, x in enumerate(self.SERVICES.keys()):
            if not ContainerRunning(x):
                return i + 1

        return 0

    def Diagnose(self, errcode):
        if errcode and self.SERVICES:
            index = errcode - 1
            service_name = self.SERVICES[list(self.SERVICES.keys())[index]]
            return (
                'Essential moblab service "%s" is not running.'
                " Please launch the service." % service_name,
                [],
            )

        return ("Unknown error reached with error code: %s" % errcode, [])


class HostScheduler(DockerContainerRunning):
    SERVICES = {"autotest-hostscheduler": "Host Scheduler"}


class JobAborter(DockerContainerRunning):
    SERVICES = {"autotest-job-aborter": "Job Aborter"}


class Scheduler(DockerContainerRunning):
    SERVICES = {"autotest-monitor-db": "Scheduler"}


class AFEServer(DockerContainerRunning):
    SERVICES = {"autotest-afe": "AFE Server"}


class Database(DockerContainerRunning):
    SERVICES = {"db": "Database"}


class Devserver(DockerContainerRunning):
    SERVICES = {"devserver": "Devserver"}


class DNS(DockerContainerRunning):
    SERVICES = {"dns": "DNS"}


class Envoy(DockerContainerRunning):
    SERVICES = {"envoy-proxy": "Envoy"}


class LogRotate(DockerContainerRunning):
    SERVICES = {"log-rotate": "Log Rotate"}


class MoblabRpcServer(DockerContainerRunning):
    SERVICES = {"moblab-rpcserver": "Moblab Rpc Server"}


class MoblabUI(DockerContainerRunning):
    SERVICES = {"moblab-ui": "Moblab UI"}


class ResultsOffloader(DockerContainerRunning):
    SERVICES = {"offloader": "Results Offloader"}


class RemoteAccess(DockerContainerRunning):
    SERVICES = {"remote_access": "Remote Access"}


class RemoteAgent(DockerContainerRunning):
    SERVICES = {"remote-agent": "Remote Agent"}


class ContainerUpdater(DockerContainerRunning):
    SERVICES = {"watchtower": "Container Updater"}


class DHCP(DockerContainerRunning):
    SERVICES = {"dhcp": "DHCP"}
