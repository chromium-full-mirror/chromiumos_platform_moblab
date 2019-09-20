# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""
from __future__ import print_function

import json
import re
import subprocess

import cachetools

from chromite.lib import cros_logging as logging

from pssh.clients import ParallelSSHClient

FIND_DUT_CMD = [
    'sudo /usr/sbin/fping -g 192.168.231.100 192.168.231.150 -c 10 -p 1 -i 1 -q'
]

SUBNET_DUT_SEARCH_RE = (r'(?P<ip>192\.168\.231\.1[0-1][0-9]) : '
                        r'xmt\/rcv\/%loss = [0-9]+\/[0-9]+\/0%.*')


class MoblabDUTConnectorException(Exception):
    pass


#ip link show | grep "state UP" | grep "mode DEFAULT"  | grep "master"
#            | awk -F ':' '{gsub(/ /, "", $2); print $2}'

#inf=$(ip link show | grep "state UP" | grep "mode DEFAULT"  | grep "master" |
#       awk -F ':' '{gsub(/ /, "", $2); print $2}')
#mac=$( cat /sys/class/net/${inf}/address)
#echo $inf $mac


class DUTInfo(object):
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
        self.connected_ip_addresses = []
        process = subprocess.Popen(
            FIND_DUT_CMD, stderr=subprocess.PIPE, shell=True)
        _, fping_result = process.communicate()
        for line in fping_result.splitlines():
            match = re.match(SUBNET_DUT_SEARCH_RE, line)
            if match:
                self.connected_ip_addresses.append(match.group('ip'))
        if process.returncode == 1:
            pass
        else:
            raise MoblabDUTConnectorException(fping_result)
        self.connected_ip_addresses = list(set(self.connected_ip_addresses))

    def reload_cache(self):
        for (ip, mac_address) in self.get_all_connected_mac():
            self.connected_duts[ip] = DUTInfo(ip, mac_address)

    def run_command_on_connected_duts(self, command):
        if not self.connected_ip_addresses:
            self.find_duts()
        return self.run_command_on_ips(command, self.connected_ip_addresses)

    def run_command_on_ips(self, command, ip_addresses):
        client = ParallelSSHClient(
            ip_addresses,
            pool_size=20,
            user='root',
            pkey='/home/moblab/.ssh/mobbase_id_rsa')
        command_results = []
        output = client.run_command(command)
        for ip, host_output in output.items():
            command_results.append((ip, [line for line in host_output.stdout]))
        logging.info('Running command %s on %s resulted in %s', command,
                     ip_addresses, command_results)
        return command_results

    def get_all_connected_mac(self):
        cmd = """
            inf=$(ip link show | grep "state UP" | grep "mode DEFAULT"  | grep "master" | awk -F ':' '{gsub(/ /, "", $2); print $2}')
            mac=$( cat /sys/class/net/${inf}/address)
            echo $mac
        """
        command_results = self.run_command_on_connected_duts(cmd)
        return [(host, output) for (host, output) in command_results]

    def get_connected_duts(self):
        command_results = self.run_command_on_connected_duts(
            'timeout 2 mosys platform model')

        def is_dut_connected(output):
            return output != None

        def extract_model(output):
            return output[0] if len(output) > 0 else 'Unknown'

        return [(host, extract_model(output), is_dut_connected(output))
                for (host, output) in command_results]

    def get_connected_dut_firmware(self):
        command_results = self.run_command_on_connected_duts(
            ('timeout 2 crossystem fwid; echo "";'
             'chromeos-firmwareupdate --manifest'))

        def get_rw_firmware(command_output):
            json_data = json.loads(''.join(command_output))
            for key in json_data.iterkeys():
                return json_data[key]['host']['versions']['rw']
            return None

        return [(host, output[0], get_rw_firmware(output[1:]))
                for (host, output) in command_results]

    def update_firmware(self, ip_addresses):
        return self.run_command_on_ips(
            'chromeos-firmwareupdate -m autoupdate; reboot', ip_addresses)
