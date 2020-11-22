# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""DUT health checks for moblab."""


import netifaces
import re

from checkfiles.moblab import common
from moblab_common.utils import cli


class DUT_CHECK_CODES:
    OK = 0
    NO_SUBNET = -1
    NO_DUTS = -2


# def list_connected_dut_ips():
#     """List duts by ip currently connected to test subnet
#
#     Returns:
#         A list of connected ips on the test subnet
#     """
#
#     # regex to search an ip n reachable or cached line such as
#     # 192.168.231.100 dev lxcbr0 lladdr 60:38:e0:e3:10:f5 STALE
#     # grabs ip, state
#     # note this will not match an 'INCOMPLETE' line that indicates
#     # no network connection
#     regex = re.compile('^(192\.168\.231\.1\d\d)\sdev\s\S+\slladdr\s\S+\s(\S+)')
#
#     duts = []
#     ip_n_output = cli.run_command(['ip', 'n']).strip()
#     for line in ip_n_output.splitlines():
#         match = regex.search(line)
#         if match is not None:
#             ip = match.group(1)
#             state = match.group(2)
#             if state == 'REACHABLE':
#                 duts.append(ip)
#             else:
#                 # a stale record, ping the ip to be sure it is reachable
#                 cmd = ['ping', '-c', '1', '-W', '1', ip]
#                 ping_output = cli.run_command(cmd, error_code_ok=True)
#                 if (ping_output is not None and
#                     '64 bytes from %s' % ip in ping_output):
#                     duts.append(ip)
#
#     return duts

# class DutExists(object):
#   """Verifies that a DUT is connected to moblab."""

#   def Check(self):
#     """Verify that at least one DUT is connected.

#     Returns:
#       OK if at least one DUT exists on moblab's test subnet.
#       NO_SUBNET if the moblab test subnet cannot be found.
#       NO_DUTS if no DUTs can be found.
#     """
#     # First, find the network interface the test subnet is connected to.
#     def FindInterface():
#       for iface in netifaces.interfaces():
#         addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
#         if not addrs:
#           continue
#         for addr in addrs:
#           if common.MOBLAB_SUBNET_ADDR == addr.get('addr'):
#             return addr['addr']

#     subnet_iface = FindInterface()

#     if not subnet_iface:
#       return DUT_CHECK_CODES.NO_SUBNET

#     duts = list_connected_dut_ips()
#     if not duts:
#       return DUT_CHECK_CODES.NO_DUTS

#     return DUT_CHECK_CODES.OK

#   def Diagnose(self, errcode):
#     if DUT_CHECK_CODES.NO_SUBNET == errcode:
#       return ('Moblab test subnet interface could not be found.', [])

#     elif DUT_CHECK_CODES.NO_DUTS == errcode:
#       return ('No DUTs were detected. Please plug in a device for test.', [])

#     return ('Unknown error reached with error code: %s' % errcode, [])
