# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""DUT health checks for moblab."""



import netifaces

from moblab import common

from util import osutils

class DUT_CHECK_CODES:
    OK = 0
    NO_SUBNET = -1
    NO_DUTS = -2

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

#     duts = osutils.list_connected_dut_ips()
#     if not duts:
#       return DUT_CHECK_CODES.NO_DUTS

#     return DUT_CHECK_CODES.OK

#   def Diagnose(self, errcode):
#     if DUT_CHECK_CODES.NO_SUBNET == errcode:
#       return ('Moblab test subnet interface could not be found.', [])

#     elif DUT_CHECK_CODES.NO_DUTS == errcode:
#       return ('No DUTs were detected. Please plug in a device for test.', [])

#     return ('Unknown error reached with error code: %s' % errcode, [])
