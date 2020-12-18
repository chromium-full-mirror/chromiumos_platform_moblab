#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""[summary]."""

import logging
import subprocess
import sys
import time
import netifaces
import os

# pylint: disable=import-error
from google.protobuf import empty_pb2
import hostservice_pb2

import host_server_base


class HostServerChromeOS(host_server_base.HostServerBase):
    """[summary]."""

    # ChromeOS update engine client binary location
    _UPDATE_ENGINE_CLIENT = "/usr/bin/update_engine_client"

    # Cache the host identifier so we do not hit VPD more that necessary.
    cached_host_identifier = None

    def get_host_identifier(self, unused_request, unused_context):
        """Get the serial number of the device from VPD.

        Use the serial number from the VPD as the host identifier, if no
        serial_number is set use the ethernet_mac value.

        Once a value has been read from the VPD cache it in memory for all
        future calls, the identifier should not change and hitting the VPD
        can be slow/error prone.

        Returns:
            HostIdentifierResponse:
                string: identifier, the host identifier.
        """
        response = hostservice_pb2.HostIdentifierResponse()
        response.identifier = "NoSerialNumber"
        if not self.cached_host_identifier:
            for vpd_key in ["serial_number", "ethernet_mac"]:
                try:
                    cmd_result = subprocess.run(
                        ["vpd", "-g", vpd_key], stdout=subprocess.PIPE
                    )
                    if (
                        cmd_result
                        and cmd_result.returncode == 0
                        and cmd_result.stdout
                    ):
                        response.identifier = cmd_result.stdout
                        self.cached_host_identifier = response.identifier
                        break
                except subprocess.SubprocessError:
                    logging.exception("Error retrieving vpd value %s", vpd_key)
        else:
            response.identifier = self.cached_host_identifier
        return response

    def get_disk_info(self, unused_request, unused_context):
        """Get information about the disk usage.

        General information about disk space usage and the disks attached
        to the chromeos device, used for debugging.

        Returns:
            DiskInfoResponse:
                string: disk_info, output of the df and lsblk commands.
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

    def get_ip(self, unused_request, unused_context):
        """Get the external IP address of the chromeos device.

        Look at all the ethernet interfaces, exclude any that are not network
        devices (virtual interfaces), exclude any that are the internal
        subnet and deduce anything else that is left is the external IP
        address.  This IP address is typically on a corportate network so it
        will be a in the private subnets, but it does not have to be.

        If more than one external interface is available it will pick just
        one and may be inconsistent as to which one is returned.

        Returns:
            IpResponse:
                string: ip_address, the external ip address found.
        """
        MOBLAB_SUBNET_ADDR = "192.168.231.1"
        response = hostservice_pb2.IpResponse()
        response.ip_address = "localhost"
        for iface in netifaces.interfaces():
            if "eth" not in iface:
                continue
            try:
                addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
            except ValueError:
                logging.warning("Non valid interface %s", iface)
                continue
            if not addrs:
                continue
            for addr in addrs:
                if MOBLAB_SUBNET_ADDR != addr.get("addr"):
                    response.ip_address = addr["addr"]
        return response

    def check_for_system_update(self, unused_request, unused_context):
        """Run the ChromeOS update client ping update server.

        If an update exists, the update client begins downloading it
        in the background.

        Returns:
            Nothing
        """
        subprocess.call([self._UPDATE_ENGINE_CLIENT, "-check_for_update"])
        # wait for update engine to finish checking
        tries = 0
        while (
            b"CHECKING_FOR_UPDATE"
            in self._get_system_update_status()[b"CURRENT_OP"]
            and tries < 10
        ):
            time.sleep(0.1)
            tries = tries + 1

        return empty_pb2.Empty()

    def _get_system_update_status(self):
        """Run the ChromeOS update client to check status.

        @return: A dictionary containing {
            PROGRESS: str containing percent progress of an update download
            CURRENT_OP: str current status of the update engine,
                ex UPDATE_STATUS_UPDATED_NEED_REBOOT
            NEW_SIZE: str size of the update
            NEW_VERSION: str version number for the update
            LAST_CHECKED_TIME: str unix time stamp of the last update check
        }
        """
        cmd_out = subprocess.check_output(
            [self._UPDATE_ENGINE_CLIENT, "--status"]
        )
        split_lines = [x.split(b"=") for x in cmd_out.strip().split(b"\n")]
        status = dict((key, val) for [key, val] in split_lines)
        return status

    def get_system_update_status(self, unused_request, unused_context):
        """Check to see if current update status.

        Call the update client to get information about an update in progress
        this can be downloading the update or ready to update.

        Returns:
            SystemUpdateStatusResponse:
                string, progress
                string, current_op
                string, new_size
                string, new_version
                string, last_checked time
        """
        response = hostservice_pb2.SystemUpdateStatusResponse()
        status = self._get_system_update_status()

        response.progress = status.get(b"PROGRESS")
        response.current_op = status.get(b"CURRENT_OP")
        response.new_size = status.get(b"NEW_SIZE")
        response.new_version = status.get(b"NEW_VERSION")
        response.last_checked_time = status.get(b"LAST_CHECKED_TIME")

        return response

    def install_system_update(self, unused_request, unused_context):
        """Installs a pending ChromeOS update.

        Call the update client to apply a downloaded chromeos update.

        This will cause the host device to reboot to finish applying the
        update.

        Returns:
            SystemUpdateInstallResponse:
                string:  error, any error information returned from the
                    update client.
        """
        response = hostservice_pb2.SystemUpdateInstallResponse()
        # first run a blocking command to check, fetch, prepare an update
        # then check if a reboot is needed
        try:
            subprocess.check_call([self._UPDATE_ENGINE_CLIENT, "--update"])
            # --is_reboot_needed returns 0 if a reboot is required
            subprocess.check_call(
                [self._UPDATE_ENGINE_CLIENT, "--is_reboot_needed"]
            )
            subprocess.call([self._UPDATE_ENGINE_CLIENT, "--reboot"])

        except subprocess.CalledProcessError:
            response.error = subprocess.check_output(
                [self._UPDATE_ENGINE_CLIENT, "--last_attempt_error"]
            )

        return response

    def reboot(self, unused_request, unused_context):
        """Reboot the moblab.

        Call the reboot script for the chromeos device.

        Returns:
            Nothing, return will never be called.
        """
        subprocess.check_call(["reboot"])
        return empty_pb2.Empty()

    def factory_reset(self, unused_request, unused_context):
        """Powerwash the moblab, resets the device removing all non OS files.

        Write the special code into the stateful partition to cause
        a powerwash on the next boot.

        Returns:
            Nothing, return will never be called.
        """
        with open(
            "/mnt/stateful_partition/factory_install_reset", "w+"
        ) as reset:
            reset.write("safe fast keepimg")
        subprocess.check_call(["reboot"])
        return empty_pb2.Empty()

    def get_system_version(self, unused_request, unused_context):
        """Get information about the current host OS version.

        Used just for information/debugging on the UI.
        Returns:
            SystemVersionResponse:
                string: track, the software track ( test, beta, stable )
                string: version, e.g. R88-12345.0.0
                string: description, descriptive string about the version.
        """
        response = hostservice_pb2.SystemVersionResponse()

        response.version = "No Version Number"
        response.track = ""
        response.description = ""

        with open("/etc/lsb-release") as f:
            lines = f.readlines()
            version_response = {
                x.split("=")[0]: x.split("=")[1] for x in lines if "=" in x
            }

            response.version = "R%s-%s" % (
                version_response["CHROMEOS_RELEASE_CHROME_MILESTONE"].strip(),
                version_response["CHROMEOS_RELEASE_VERSION"].strip(),
            )
            response.track = version_response["CHROMEOS_RELEASE_TRACK"]
            response.description = version_response[
                "CHROMEOS_RELEASE_DESCRIPTION"
            ]

        return response

    def get_disk_usage_stats(self, request, context):
        """Get information about available disk space.

        Returns:
            GetDiskUsageStatsResponse:
                free_MB: amount of available disk space in MB.
        """

        disk_stats = [
            s.split()
            for s in os.popen("df -BM | grep stateful_partition")
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
        response.available_MB = int(disk_stats[3].rtrim("M"))
        response.total_MB = int(disk_stats[1].rtrim("M"))
        return response


class DiskSpaceException(Exception):
    """Exception thrown by get_disk_space endpoint"""

    pass


if __name__ == "__main__":
    host_server = HostServerChromeOS()
    host_server.serve(sys.argv[1:])
