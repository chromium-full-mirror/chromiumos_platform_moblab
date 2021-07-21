# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""

import json
import logging
import os
import ssh2
import subprocess
import re

from pssh.clients.native.parallel import ParallelSSHClient
import pssh


# Location where dhcp leases are stored.
_DHCPD_LEASES = "/leases/dnsmasq.leases"

# fping, ping a range of IP addresses in parallel.
# -c is the number of packets to send.
# -p is the interval between ping packets to a single target.
# -i is the interval between sending ping packets.
FIND_DUT_CMD = [
    "cat %s | awk -F ' ' '{print $3}' | /usr/bin/fping -a" % _DHCPD_LEASES
]

SUBNET_DUT_SEARCH_RE = r"(?P<ip>192\.168\.231\.[0-9][0-9]*[0-9]*).*"


class MoblabDUTConnectorException(Exception):
    """Generic exception for this module."""

    pass


class DUTInfo(object):
    """Class to encapsulate the information for a single DUT."""

    mac_address = None
    ip_addresses = None

    def __init__(self, ip_address, mac_address):
        ip_address = ip_address
        mac_address = mac_address


class MoblabDUTConnector(object):
    """TODO ADD DOC"""

    def __init__(self):
        self.connected_ip_addresses = []
        self.disconnected_ip_addresses = []

    def find_duts(self):
        active_hosts = self._get_active_network_devices()
        self.connected_ip_addresses = []
        self.disconnected_ip_addresses = []
        for host in list(self._get_dhcp_dut_leases()):
            if host in active_hosts:
                self.connected_ip_addresses.append(host)
            else:
                self.disconnected_ip_addresses.append(host)
                logging.warning("Rejecting %s from %s", host, active_hosts)

    def _get_dhcp_dut_leases(self):
        """Extract information about connected duts from the dhcp server.

        @return: A dict of ipaddress to mac address for each device connected.
        """
        if not os.path.exists(_DHCPD_LEASES):
            return {}
        lease_lines = open(_DHCPD_LEASES).readlines()

        # Lease lines look like this:
        # 1584225109 60:38:e0:e3:10:bd 192.168.231.113 * 01:60:38:e0:e3:10:bd
        leases = {}
        for lease in lease_lines:
            items = lease.strip().split(" ")
            leases[items[2]] = items[1]
        return leases

    def run_command_on_connected_duts(self, command, timeout=300):
        self.find_duts()
        return self.run_command_on_ips(
            command, self.connected_ip_addresses, timeout
        )

    def run_command_on_ips(self, command, ip_addresses, timeout=10):
        client = ParallelSSHClient(
            ip_addresses,
            pool_size=20,
            user="root",
            num_retries=1,
            keepalive_seconds=timeout,
            timeout=timeout,
            pkey="/home/moblab/.ssh/testing_rsa",
        )
        command_results = []

        output = client.run_command(
            command, stop_on_errors=False, timeout=timeout
        )
        try:
            client.join(output)
            for host_output in output:
                stdout = (
                    "{}".format("\n".join(host_output.stdout))
                    if host_output.stdout
                    else ""
                )
                stderr = (
                    "{}".format("\n".join(host_output.stderr))
                    if host_output.stderr
                    else ""
                )

                # Extracts details from host_output.exception to construct an
                # error message.
                try:
                    if host_output.exception:
                        logging.info(
                            "Found a host output exception: %s",
                            host_output.exception,
                        )
                        exception_msg = host_output.exception.args[0]
                        exception_args = host_output.exception.args[1:]
                        stderr += exception_msg % exception_args
                except IndexError:
                    logging.exception(
                        "Failed to extract information from "
                        + "host_output.exception: %s",
                        host_output.exception,
                    )
                except TypeError:
                    logging.exception(
                        "Failed to construct the stderr from "
                        + "host_output.exception: %s",
                        host_output.exception,
                    )

                command_results.append(
                    (host_output.host, stdout, stderr, host_output.exit_code)
                )
            logging.info(
                "Running command %s on %s resulted in %s",
                command,
                ip_addresses,
                command_results,
            )
        except ssh2.exceptions.SocketRecvError:
            logging.exception("Command failed to run %s", command)
        except pssh.exceptions.Timeout:
            logging.exception("Command failed to run %s", command)
        return command_results

    def get_all_known_mac_addresses(self):
        return self._get_dhcp_dut_leases()

    def _get_active_network_devices(self):
        connected_ip_addresses = []
        process = subprocess.run(FIND_DUT_CMD, capture_output=True, shell=True)
        # TODO: Research the return codes and do something smart with them.
        # process.check_returncode()
        fping_result = process.stdout
        for line in fping_result.decode("utf-8").splitlines():
            match = re.match(SUBNET_DUT_SEARCH_RE, line)
            if match:
                connected_ip_addresses.append(match.group("ip"))
            else:
                logging.info("Ignoring %s no match" % line)
        return list(set(connected_ip_addresses))

    def get_connected_duts(self):
        command_results = self.run_command_on_connected_duts(
            "timeout 2 cat /etc/lsb-release", timeout=10
        )

        def is_dut_connected(output):
            if output:
                return output is not None
            return False

        results = []
        for (host, stdout, stderr, _) in command_results:
            results.append((host, is_dut_connected(stdout), stderr))
        return results

    def get_connected_dut_firmware(self):
        """Get current and firmware update on each DUT.

           Gets the currently installed firmware on the DUT.
           Looks at the install manifest to the firmware ID that would
           be installed with a firmware update command.

           The installed firmware and the update firmware may be the same.
        Returns:
            list: list of tuples each tuple contains:
                 string: host, the ip address if the DUT
                 string: current firmware, version of installed firmware
                 string: update firmware, version of firmware to be applied.
        """
        command_results = self.run_command_on_connected_duts(
            (
                "fwid=`timeout 5 crossystem fwid`;"
                "model=`timeout 5 mosys platform model`;"
                "fw_update=`timeout 5 chromeos-firmwareupdate --manifest`;"
                'printf "{\\"fwid\\": \\"%s\\",\\"model\\": \\"%s\\",'
                '\\"fw_update\\":%s}" $fwid $model "$fw_update"'
            ),
            timeout=20,
        )

        results = []
        for (host, stdout, stderr, exit_code) in command_results:
            if exit_code:
                results.append((host, stderr, stderr))
            else:
                try:
                    parsed_results = json.loads(stdout)
                except json.JSONDecodeError as e:
                    logging.exception("Failed to decode fw details %s", stdout)
                    results.append((host, e.msg, stderr))
                    continue
                model = parsed_results["model"]
                current_firmware = parsed_results["fwid"]
                firmware_update = parsed_results["fw_update"][model]["host"][
                    "versions"
                ]["rw"]
                results.append((host, current_firmware, firmware_update))
        return results

    def update_firmware(self, ip_addresses):
        command_results = self.run_command_on_ips(
            ("/usr/sbin/chromeos-firmwareupdate --mode autoupdate --force"),
            ip_addresses,
            timeout=120,
        )
        self.run_command_on_ips("reboot", ip_addresses)
        return command_results

    def get_connected_dut_serialno(self):
        """
            Will attempt to read serial numbers for all connected duts.
        Returns:
            Tuple pairs where the first item is the hostname (IP) and the second
            item is the parsed serial number.
        """
        command_results = self.run_command_on_connected_duts(
            "timeout 20 vpd -g serial_number", timeout=20
        )
        results = []
        for (host, stdout, stderr, exit_code) in command_results:
            if exit_code:
                results.append(
                    (host, "Failed to parse s/n for {}".format(host))
                )
                logging.error(
                    "Attempted to discover serial numbers "
                    "of {} exited with error: {}".format(host, stderr)
                )
            else:
                results.append((host, stdout))
        return results

    def get_disconnected_dut_ips(self):
        """Gets the IP address of the disconnected DUTs.

        Returns:
            Tuple of IP addresses.
        """
        self.find_duts()
        return self.disconnected_ip_addresses
