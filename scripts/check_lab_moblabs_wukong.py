#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import sys
import paramiko

CHECK_SCRIPT = """
    rm -f /mnt/moblab-settings/dhcpd-reservations_generated.conf
    host_dut=1
    IFS=$'\n'
    for line in $( ip n show dev lxcbr0 | sort ); do
       unset IFS
       read ip mac <<< $( echo $line | awk -F' ' '{print $1 " " $3}' )
       read ping_result <<< $( ping -c1 -W1 $ip | awk -F',' '{print $3}' )
       if [ "$ping_result" == "0% packet loss" ]; then
          echo "host dut$host_dut {" >> /mnt/moblab-settings/dhcpd-reservations_generated.conf
          echo "  hardware ethernet $mac;" >> /mnt/moblab-settings/dhcpd-reservations_generated.conf
          echo "  fixed-address $ip;" >> /mnt/moblab-settings/dhcpd-reservations_generated.conf
          echo "}" >> /mnt/moblab-settings/dhcpd-reservations_generated.conf
          echo "" >> /mnt/moblab-settings/dhcpd-reservations_generated.conf
          host_dut=$((host_dut + 1))
       fi
    done
    cat /mnt/moblab-settings/dhcpd-reservations_generated.conf
    sdiff -s /mnt/moblab-settings/dhcpd-reservations.conf /mnt/moblab-settings/dhcpd-reservations_generated.conf
"""

# CHECK_SCRIPT = """
#    sudo rm -rf /mnt/moblab/containers
#    sudo reboot
#
# """

# CHECK_SCRIPT = """
#    sudo reboot
# """

# CHECK_SCRIPT = """
#    ls -lrt /mnt/moblab/containers
# """

# CHECK_SCRIPT = """
#    ssh root@192.168.231.100 'chromeos-firmwareupdate --mode=autoupdate'
#    ssh root@192.168.231.101 'chromeos-firmwareupdate --mode=autoupdate'
# """

# CHECK_SCRIPT = """
#    ssh root@192.168.231.100 'reboot'
#    ssh root@192.168.231.101 'reboot'
# """

# CHECK_SCRIPT = """
#   sudo chromeos-firmwareupdate --mode=autoupdate
# """

# CHECK_SCRIPT = """
#   sudo chown -R moblab:moblab /mnt/moblab/containers
# """

MOBLAB_USER_ACCOUNT = 'moblab'


def run_script_on_moblab_host(hostname, script, key):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    output = ""
    try:
        client.connect(
            hostname=hostname,
            username=MOBLAB_USER_ACCOUNT,
            key_filename=os.environ['HOME'] + '/.ssh/testing_rsa',
            timeout=15)
    except Exception as e:
        output = str(e)
    else:
        stdin, stdout, stderr = client.exec_command(script, timeout=15)
        try:
            output = stdout.read()
            output += stderr.read()
        except Exception as e:
            output = str(e)
    finally:
        client.close()
    return output


if __name__ == '__main__':
    domain = 'cros.corp.google.com'
    hosts = [
        'chromeos2-row1-rack7-host1',
        'chromeos2-row1-rack7-host3',
        'chromeos2-row1-rack7-host5',
        'chromeos2-row1-rack7-host7',
        'chromeos2-row1-rack7-host9',
        'chromeos2-row1-rack7-host11',
        'chromeos2-row2-rack7-host1',
        'chromeos2-row2-rack7-host3',
        'chromeos2-row2-rack7-host5',
        'chromeos2-row2-rack7-host7',
        'chromeos2-row2-rack7-host9',
        'chromeos2-row1-rack8-host1',
        'chromeos2-row1-rack8-host3',
        'chromeos2-row2-rack8-host1',
        'chromeos2-row2-rack8-host3',
        'chromeos2-row2-rack8-host5',
        'chromeos2-row2-rack8-host7',
        'chromeos2-row2-rack8-host9',
        'chromeos2-row2-rack8-host11',
    ]
    key_file = os.path.expanduser(
        os.path.join(os.environ['HOME'], '.ssh', 'testing_rsa'))
    for host in hosts:
        output = run_script_on_moblab_host(host + '.' + domain, CHECK_SCRIPT,
                                           key_file)
        output.strip()
        if output != None:
            print '////////////////////////////////////////////////////////'
            print host
            print output
