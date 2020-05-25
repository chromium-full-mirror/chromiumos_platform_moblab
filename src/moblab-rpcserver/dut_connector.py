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
from pssh.clients import ParallelSSHClient


# Location where dhcp leases are stored.
_DHCPD_LEASES = '/leases/dnsmasq.leases'

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
         logging.info(list(self._get_dhcp_dut_leases()))
         self.connected_ip_addresses = list(self._get_dhcp_dut_leases())

    def _get_dhcp_dut_leases(self):
     """ Extract information about connected duts from the dhcp server.

     @return: A dict of ipaddress to mac address for each device connected.
     """
     if not os.path.exists(_DHCPD_LEASES):
         return {}
     lease_lines = open(_DHCPD_LEASES).readlines()

     # Lease lines look like this:
     # 1584225109 60:38:e0:e3:10:bd 192.168.231.113 * 01:60:38:e0:e3:10:bd
     leases = {}
     for lease in lease_lines:
         items = lease.strip().split(' ')
         leases[items[2]] = items[1]
     return leases

    def reload_cache(self):
        for (ip, mac_address) in self.get_all_connected_mac():
            self.connected_duts[ip] = DUTInfo(ip, mac_address)

    def run_command_on_connected_duts(self, command, timeout=300):
        if not self.connected_ip_addresses:
            self.find_duts()
        return self.run_command_on_ips(command, self.connected_ip_addresses,
                                       timeout)

    def run_command_on_ips(self, command, ip_addresses, timeout=300):
        client = ParallelSSHClient(
            ip_addresses,
            pool_size=20,
            user='root',
            num_retries=1,
            timeout=10,
            pkey='/home/moblab/.ssh/testing_rsa')
        command_results = []

        output = client.run_command(command, stop_on_errors=False, timeout=10)

        for ip, host_output in output.items():
            stdout = ''
            if host_output.stdout:
                stdout = [line for line in host_output.stdout]
            stderr = ''
            if host_output.exception:
                stderr = host_output.exception[0] % host_output.exception[1:]
            command_results.append((ip, stdout, stderr))
        logging.info('Running command %s on %s resulted in %s', command,
                     ip_addresses, command_results)
        return command_results

    def get_all_connected_mac(self):
        leases = self._get_dhcp_dut_leases()
        return [(host, output) for (host, output) in leases.items()]

    def get_connected_duts(self):
        command_results = self.run_command_on_connected_duts(
            'timeout 100 mosys platform model', timeout=100)

        def is_dut_connected(output):
            if output:
                return output != None
            return False

        def extract_model(output):
            return output[0] if output else 'Unknown'

        return [(host, extract_model(stdout), is_dut_connected(stdout), stderr)
                for (host, stdout, stderr) in command_results]

    def get_connected_dut_firmware(self):
        command_results = self.run_command_on_connected_duts(
            ('timeout 10 crossystem fwid; echo ""; '
             'mosys platform model;'
             'chromeos-firmwareupdate --manifest'))

        def get_rw_firmware(command_output, model):
            logging.info(model)
            json_data = json.loads(''.join(command_output))
            return json_data[model]['host']['versions']['rw']
            return None

        return [(host, output[0], get_rw_firmware(output[2:], output[1]))
                for (host, output, stderr) in command_results]

    def update_firmware(self, ip_addresses):
        return self.run_command_on_ips(
            'chromeos-firmwareupdate -m autoupdate; reboot', ip_addresses)

    def get_connected_dut_serialno(self):
        command_results = self.run_command_on_connected_duts(
            'timeout 20 vpd -g serial_number', timeout=20)
        return [(host, output[0]) for (host, output, stderr) in command_results]
