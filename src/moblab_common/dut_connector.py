# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the AFE RPC server for all moblab code."""
from __future__ import print_function

import subprocess
import re
import json

from pssh.clients import ParallelSSHClient

FIND_DUT_CMD = [
    'sudo /usr/sbin/fping -g 192.168.231.100 192.168.231.150 -c 10 -p 1 -i 1 -q'
]

SUBNET_DUT_SEARCH_RE = (r'(?P<ip>192\.168\.231\.1[0-1][0-9]) : '
                        'xmt\/rcv\/%loss = [0-9]+\/[0-9]+\/0%.*')


class MoblabDUTConnectorException(Exception):
    pass


class MoblabDUTConnector(object):
    """TODO ADD DOC"""

    def __init__(self):
        self.hosts = []

    def find_duts(self):
        self.hosts = []
        process = subprocess.Popen(
            FIND_DUT_CMD, stderr=subprocess.PIPE, shell=True)
        _, fping_result = process.communicate()
        for line in fping_result.splitlines():
            match = re.match(SUBNET_DUT_SEARCH_RE, line)
            if match:
                self.hosts.append(match.group('ip'))
        if process.returncode == 1:
            pass
        else:
            raise MoblabDUTConnectorException(fping_result)

    def run_command_on_connected_dut(self, command):
        client = ParallelSSHClient(
            self.hosts,
            pool_size=20,
            user='root',
            pkey='/home/moblab/.ssh/mobbase_id_rsa')
        command_results = []
        output = client.run_command(command)
        for host, host_output in output.items():
            command_results.append((host,
                                    [line for line in host_output.stdout]))
        return command_results

    def get_all_connected_mac(self):
        cmd = ('inf=$(ip link show | grep "state UP" | grep "mode DEFAULT"  | '
               'grep "master" | awk -F ":" "{gsub(/ /, "", $2); print $2}") '
               'mac=$( cat /sys/class/net/${inf}/address) '
               'echo $mac')
        command_results = self.run_command_on_connected_dut(cmd)
        return [(host, output) for (host, output) in command_results]

    def get_connected_duts(self):
        command_results = self.run_command_on_connected_dut(
            'timeout 2 cat /etc/lsb-release; ifconfig eth0 | grep ether')

        def is_dut_connected((host, host_output)):
            return (host, 'CHROMEOS_RELEASE_APPID' in host_output)

        return [(host, is_dut_connected(output))
                for (host, output) in command_results]

    def get_connected_dut_firmware(self):
        cmd = ('timeout 2 crossystem fwid; echo "";chromeos-firmwareupdate ',
               '--manifest')
        command_results = self.run_command_on_connected_dut(cmd)

        def get_rw_firmware(command_output):
            json_data = json.loads(''.join(command_output))
            for key in json_data.iterkeys():
                return json_data[key]['host']['versions']['rw']
            return None

        return [(host, output[0], get_rw_firmware(output[1:]))
                for (host, output) in command_results]
