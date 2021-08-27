#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""GRPC server that provides host service to docker containers on debian."""

import logging
import subprocess
import sys
import netifaces
import hostservice_pb2
import host_server_base


from utils import cpu_temperature_orchestrator

_LOGGER = logging.getLogger("host-server")


class HostServerDebian(host_server_base.HostServerBase):
    """Implementation for the hostservice contract on debian.

    It has been specifically chosen to not implement reboot, reset or update
    as on debian these should be performed outside of the moblab software.

    As debian machines can serve other functions than just running moblab like
    being a development machine this implementation should only implement
    read only functions as providing a non authenticated way for someone to
    perform write / destructive operations on such as machine as root user
    is undesirable.
    """

    # CpuTemperatureOrchestrator instance.
    _cpu_temp = cpu_temperature_orchestrator.CpuTemperatureOrchestrator(30, 1)

    def get_host_identifier(self, unused_request, unused_context):
        """Get a stable identifier for the machine.

        This identifier should be as stable as possible, it is used in
        CPCon to tie different install id's of the moblab software together
        and makes it possible to give a user defined name to the moblab device
        in the remote console.

        Returns:
            string: the value in /etc/machine id or "NoSerialNumber".
        """
        response = hostservice_pb2.HostIdentifierResponse()
        response.identifier = "NoSerialNumber"
        # This can change on OS re-install.
        cmd = ["cat /etc/machine-id"]
        try:
            cmd_result = subprocess.run(
                cmd, stdout=subprocess.PIPE, shell=True
            )

            if cmd_result and cmd_result.returncode == 0 and cmd_result.stdout:
                response.identifier = cmd_result.stdout.decode("utf-8").strip()
        except subprocess.SubprocessError:
            logging.exception("Error retrieving machine id")
        return response

    def get_disk_info(self, unused_request, unused_context):
        """Return a string that shows information about disk usage.

        This string is displayed in mobmonitor and no guarantee of the format
        is given so it should not be parsed by the client.

        Returns:
            string: Information about the disk usage of the host machine.
        """
        result = "df -h\n"
        cmd = ["df -h | sort -r -k 5 -i | grep dev"]
        cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        if cmd_result and cmd_result.returncode == 0 and cmd_result.stdout:
            result += cmd_result.stdout.decode("utf-8")

        result += "\nlsblk\n"
        cmd = ["lsblk"]
        cmd_result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        if cmd_result and cmd_result.returncode == 0 and cmd_result.stdout:
            result += cmd_result.stdout.decode("utf-8")

        response = hostservice_pb2.DiskInfoResponse()
        response.disk_info = result
        return response

    def get_cpu_temperature(self, unused_request, unused_context):
        """Get average CPU temperature over the last 30 minutes."""
        response = hostservice_pb2.CpuTemperatureResponse()
        temp = HostServerDebian._cpu_temp.get_average_cpu_temperature()
        if not isinstance(temp, float):
            _LOGGER.error(
                "Received temperature value is %s which "
                "is not of type float." % str(temp)
            )
            temp = float(0)
        response.temperature = temp
        return response

    def get_ip(self, unused_request, unused_context):
        """Get the host machines IP address on the network.

        Find the address the host machine connects to the internet and
        return that value.

        Returns:
            string: network address of the host.
        """
        MOBLAB_SUBNET_ADDR = "192.168.231.1"
        response = hostservice_pb2.IpResponse()
        response.ip_address = "localhost"
        for iface in netifaces.interfaces():
            if "enp" not in iface:
                continue
            addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
            if not addrs:
                continue
            for addr in addrs:
                if MOBLAB_SUBNET_ADDR != addr.get("addr"):
                    response.ip_address = addr["addr"]
        return response

    def get_system_version(self, unused_request, unused_context):
        """Get version string of the host machines OS.

        Returns:
            string: An information string about the version of the host os.
        """
        response = hostservice_pb2.SystemVersionResponse()

        response.version = "No Version Number"
        try:
            with open("/etc/debian_version") as f:
                response.version = "".join(f.readlines()).strip()
        except (FileNotFoundError, IOError):
            logging.exception("Error retrieving version number")

        response.track = ""
        response.description = ""

        try:
            with open("/etc/os-release") as f:
                output = f.readlines()
                os_release_info = {}
                for line in output:
                    (key, value) = line.split("=")
                    os_release_info[key] = value.strip('"\n')
                response.track = os_release_info.get(
                    "VERSION_CODENAME", "No Track Found"
                )
                response.description = os_release_info.get(
                    "PRETTY_NAME", "No Name Found"
                )
        except (FileNotFoundError, IOError):
            logging.exception("Error retrieving version information")

        return response

    def get_disk_usage_stats(self, request, context):
        """Get information about available disk space.

        Returns:
            GetDiskUsageStatsResponse:
                free_MB: amount of available disk space in MB.
        """
        if not self.docker_dir:
            cmd = ["docker info | grep 'Root Dir'"]
            cmd_result = subprocess.run(
                cmd, stdout=subprocess.PIPE, shell=True
            )
            self.docker_dir = cmd_result.stdout.split(b": ")[1].strip()
        disk_stats = [
            s.split()
            for s in os.popen("df -BM %s" % self.docker_dir)
            .read()
            .splitlines()
        ]
        # Ex. output:
        # Filesystem   1M-blocks    Used Available Use% Mounted on
        # /dev/mmcblk0   790388M 168009M   582163M  23% /
        # ...
        if len(disk_stats) != 1:
            raise DiskSpaceException(
                "%s stateful partitions found, expected one" % len(disk_stats)
            )
        disk_stats = disk_stats[0]

        response = hostservice_pb2.GetDiskUsageStatsResponse()
        response.available_MB = int(disk_stats[3].rstrip("M"))
        response.total_MB = int(disk_stats[1].rstrip("M"))
        return response


if __name__ == "__main__":
    host_server = HostServerDebian()
    host_server.serve(sys.argv[1:])
