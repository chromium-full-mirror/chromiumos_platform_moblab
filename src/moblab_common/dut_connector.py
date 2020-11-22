# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""

import json
import logging
import os
import re
import subprocess


import cachetools
import nmap
from pssh.clients.native import ParallelSSHClient


# Location where dhcp leases are stored.
_DHCPD_LEASES = "/leases/dnsmasq.leases"


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
        self.connected_duts = cachetools.TTLCache(25, 30 * 60)

    def find_duts(self):
        active_hosts = self._get_active_network_devices()
        self.connected_ip_addresses = []
        for host in list(self._get_dhcp_dut_leases()):
            if host in active_hosts:
                self.connected_ip_addresses.append(host)
            else:
                logging.info("Rejecting %s %s", host, active_hosts)

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

    def reload_cache(self):
        for (ip, mac_address) in self.get_all_connected_mac():
            self.connected_duts[ip] = DUTInfo(ip, mac_address)

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
            timeout=timeout,
            pkey="/home/moblab/.ssh/testing_rsa",
        )
        command_results = []

        output = client.run_command(
            command, stop_on_errors=False, timeout=timeout
        )
        client.join(output)

        for host_output in output:
            stdout = (
                "{}".format("".join(host_output.stdout))
                if host_output.stdout
                else ""
            )
            stderr = (
                "{}".format("".join(host_output.stderr))
                if host_output.stderr
                else ""
            )

            exit_code = host_output.exit_code

            if host_output.exception:
                exception_msg = host_output.exception.args[0]
                exception_args = host_output.exception.args[1:]
                stderr += exception_msg % exception_args
            command_results.append(
                (host_output.host, stdout, stderr, exit_code)
            )
        logging.info(
            "Running command %s on %s resulted in %s",
            command,
            ip_addresses,
            command_results,
        )
        return command_results

    def get_all_connected_mac(self):
        leases = self._get_dhcp_dut_leases()
        active_hosts = self._get_active_network_devices()
        return [
            (host, output)
            for (host, output) in leases.items()
            if host in active_hosts
        ]

    def _get_active_network_devices(self):
        """Use the tool nmap to find devices currently alive on the network.

        Nmap docs https://nmap.org/docs.html
        It is a network port scanner.

        Docker containers have issues with ping, considered a admin tool
        it is unreliable for containers not running as root.

        nmap command:   Pn - do not use ping discovery
                        T 5 - be fast / fewer retries
                        22 scan only port 22
                        Scan the full DUT IP range 192.168.231.0/24'

        Returns:
            list: A list of IP addresses with port 22 open and active.
        """
        nm = nmap.PortScanner()
        nm.scan("192.168.231.0/24", "22", "-T 5 --open -Pn")
        hosts = nm.all_hosts()
        return hosts

    def get_connected_duts(self):
        command_results = self.run_command_on_connected_duts(
            "timeout 2 cat /etc/lsb-release", timeout=100
        )

        def is_dut_connected(output):
            if output:
                return output != None
            return False

        def extract_model(output):
            return output[0] if output else "Unknown"

        results = []
        for (host, stdout, stderr, exit_code) in command_results:
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
                "fwid=`timeout 10 crossystem fwid`;"
                "model=`timeout 10 mosys platform model`;"
                "fw_update=`timeout 20 chromeos-firmwareupdate --manifest`;"
                'printf "{\\"fwid\\": \\"%s\\",\\"model\\": \\"%s\\",'
                '\\"fw_update\\":%s}" $fwid $model "$fw_update"'
            ),
            timeout=50,
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
            (
                "/usr/sbin/chromeos-firmwareupdate --mode autoupdate "
                "--force --verbose"
            ),
            ip_addresses,
            timeout=300,
        )
        self.run_command_on_ips("reboot", ip_addresses)
        return command_results

    def get_connected_dut_serialno(self):
        """
            Will attempt to read serial numbers for all connected duts.
        Returns:
            Tuple pairs where the first item is the hostname (IP) and the second item
            is the parsed serial number.
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
                    "Attempted to discover serial no of {} exited with error: {}".format(
                        stderr
                    )
                )
            else:
                results.append((host, stdout))
        return results
