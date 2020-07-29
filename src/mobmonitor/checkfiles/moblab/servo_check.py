# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Servo health checks for moblab."""



from moblab_common.utils import cli

SERVO_VID = b'18d1'
SERVO_PID = [b'5002', b'501b']


# class ServoExists(object):
#   """Verfies that a Servo is connected to moblab."""

#   def Check(self):
#     """Verify that a Servo is connected.

#     Returns:
#       0 if a Servo exists.
#       1 if a Servo device could not be found.
#     """
#     cmd = ['lsusb']
#     usbs = cli.sudo_run_command(cmd).strip()
#     for pid in SERVO_PID:
#       servo_id = b'%s:%s' % (SERVO_VID, pid)
#       for usb in usbs.split(b'\n'):
#         if servo_id in usb:
#           return 0
#     return 1

#   def Diagnose(self, errcode):
#     if 1 == errcode:
#       return ('No servo devices are connected.', [])

#     return ('Unknown error reached with error code: %s' % errcode, [])
