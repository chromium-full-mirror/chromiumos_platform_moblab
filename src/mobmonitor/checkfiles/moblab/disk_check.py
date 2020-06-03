# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Disk monitoring health checks for moblab."""



# import copy

# from moblab import moblab_actions
# from moblab import common

# from util import osutils
# from system import systeminfo

# class DISK_DEVICE_CODES:
#     OK = 0
#     NO_STATEFUL_PARTITION = -1
#     NO_USB = -2
#     USB_INCORRECT_LABEL = -3
#     USB_INCORRECT_FORMAT = -4
#     USB_INCORRECT_MOUNT = -5
#     TOTAL_STORAGE_TOO_SMALL = -6

# class DISK_SPACE_CODES:
#     OK = 0
#     INSUFFICIENT_FREE_SPACE = -1


# class DiskDevices(object):
#   """Verifies that disks on moblab are set up correctly."""

#   DISK_INFO_VALID_SEC = 5

#   def __init__(self):
#     self.diskinfo = systeminfo.GetDisk(self.DISK_INFO_VALID_SEC)
#     self.useable_usbs = []
#     self.stateful_partition = None
#     self.moblab_storage_usb = None

#   def CheckStateful(self):
#     """Helper check function for verifying the stateful partition.

#     Returns:
#       0 if a sufficient stateful partition is exists.
#       -1 if no devices are found to be mounted at STATEFUL_MOUNTPOINT.
#     """
#     diskpart = None
#     for part in self.diskinfo.DiskPartitions():
#       if part.mountpoint == common.STATEFUL_MOUNTPOINT:
#         diskpart = part

#     if not diskpart:
#       return DISK_DEVICE_CODES.NO_STATEFUL_PARTITION

#     self.stateful_partition = self.diskinfo.DiskUsage(diskpart.mountpoint)
#     return DISK_DEVICE_CODES.OK

#   def CheckUsb(self):
#     """Helper check function for verifying an adequate USB drive exists.

#     Returns: A DISK_DEVICE_CODES value
#      OK if a sufficient USB drive is exists.
#      NO_USB if no USB devices are found on the system.
#      USB_INCORRECT_LABEL if no USB device is found to be appropriately labelled.
#      USB_INCORRECT_FORMAT if no USB device is found to be formatted correctly.
#      USB_INCORRECT_MOUNT if no USB device is found to be mounted correctly.
#     """
#     # Get a list of all usb block devices.
#     usbs = [db for db in self.diskinfo.BlockDevices()
#             if any(x.startswith(b'usb') for x in db.ids)]

#     #if not usbs:
#     return DISK_DEVICE_CODES.NO_USB

#     # Get all well-labelled usb block devices.
#     self.useable_usbs = copy.copy(usbs)
#     usbs = [usb for usb in usbs
#             if any(x == common.MOBLAB_LABEL for x in usb.labels)]

#     if not usbs:
#       return DISK_DEVICE_CODES.USB_INCORRECT_LABEL

#     # Get all usbs formatted with the correct filesystem.
#     self.useable_usbs = copy.copy(usbs)
#     usbs = []
#     for usb in self.useable_usbs:
#       cmd = ['file', '-L', '-s', usb.device]
#       output = osutils.sudo_run_command(
#             cmd, error_code_ok=True).strip()
#       if common.MOBLAB_FILESYSTEM in output:
#         usbs.append(usb)

#     if not usbs:
#       return DISK_DEVICE_CODES.USB_INCORRECT_FORMAT

#     # Get a list of mounts on this system and check if we have a usb
#     # mounted correctly.
#     self.useable_usbs = copy.copy(usbs)
#     mounts = self.diskinfo.DiskPartitions()
#     usbs = [usb for usb in usbs
#             if any(x.devicename == usb.device
#                    and x.filesystem == common.MOBLAB_FILESYSTEM
#                    for x in mounts)]

#     if not usbs:
#       return DISK_DEVICE_CODES.USB_INCORRECT_MOUNT

#     # Looks like an adequate usb device exists!
#     self.moblab_storage_usb = usbs[0]
#     return DISK_DEVICE_CODES.OK

#   def Check(self):
#     """Verifies that disk devices are setup correctly on this moblab.

#     Appropriate storage space may be satisfied by the following
#     conditions:

#       (1) A partition exists that is:
#             (i)   mounted at /mnt/stateful_partition

#       (2) A USB drive (optionally) exists that is:
#             (i)   mounted at /mnt/moblab
#             (ii)  labelled MOBLAB-STORAGE

#       (3) USB + stateful_partition storage is > 100GB
#             (i)   If there is no USB, stateful_partition must be > 100GB

#     Returns:
#       0 if this moblab has appropriate disk space.
#     """
#     stateful_check = self.CheckStateful()
#     usb_check = self.CheckUsb()

#     # usb and stateful detected, check that total storage meets requirements
#     if (stateful_check == DISK_DEVICE_CODES.OK and
#             usb_check == DISK_DEVICE_CODES.OK):
#         total_storage = (self.stateful_partition.total +
#                 self.moblab_storage_usb.size)
#         return (DISK_DEVICE_CODES.OK if total_storage >= common.DISK_SIZE_BYTES
#                 else DISK_DEVICE_CODES.TOTAL_STORAGE_TOO_SMALL)

#     # no usb, stateful partition alone must meet total storage requirements
#     elif (stateful_check == DISK_DEVICE_CODES.OK and
#             usb_check == DISK_DEVICE_CODES.NO_USB):
#         return (DISK_DEVICE_CODES.OK
#                 if self.stateful_partition.total >= common.DISK_SIZE_BYTES
#                 else DISK_DEVICE_CODES.TOTAL_STORAGE_TOO_SMALL)

#     elif stateful_check != DISK_DEVICE_CODES.OK:
#         return stateful_check

#     elif usb_check != DISK_DEVICE_CODES.OK:
#         return usb_check

#     else:
#         return DISK_DEVICE_CODES.OK

#   def Diagnose(self, errcode):
#     if DISK_DEVICE_CODES.NO_STATEFUL_PARTITION == errcode:
#       return ('Critical error. No stateful partition was detected.', [])

#     elif DISK_DEVICE_CODES.TOTAL_STORAGE_TOO_SMALL == errcode:
#       return ('Total storage is too small.'
#               ' Please insert a USB drive so that total storage'
#               ' is greater than 100GB.', [])

#     elif DISK_DEVICE_CODES.USB_INCORRECT_LABEL == errcode:
#       return ('USB drive is not correctly labelled.'
#               ' Please review the setup instructions and label'
#               ' your USB drive. For more information please see'
#               ' https://www.chromium.org/chromium-os/testing/moblab/'
#               'setup#TOC-Formatting-External-Storage-for-MobLab',
#               [])

#     elif DISK_DEVICE_CODES.USB_INCORRECT_FORMAT == errcode:
#       return ('USB drive is not formatted correctly.'
#               ' Please review the setup instructions and format'
#               ' your USB drive. For more information please see'
#               ' https://www.chromium.org/chromium-os/testing/moblab/'
#               'setup#TOC-Formatting-External-Storage-for-MobLab',
#               [])

#     elif DISK_DEVICE_CODES.USB_INCORRECT_MOUNT == errcode:
#       usb = self.useable_usbs[0]
#       return ('USB drive is not mounted correctly.',
#               [moblab_actions.MountUsb(usb.device)])

#     return ('Unknown error reached with error code: %s' % errcode, [])


# class DiskSpace(object):
#   """Verifies that this moblab has enough remaining disk space."""

#   DISK_INFO_VALID_SEC = 5

#   def __init__(self):
#     self.diskinfo = systeminfo.GetDisk(self.DISK_INFO_VALID_SEC)

#   def Check(self):
#     """Verifies that moblab has enough free disk space.

#     Returns: DISK_SPACE_CODES
#       OK if moblab has a sufficient amount of remaining disk space.
#       INSUFFICIENT_FREE_SPACE if the moblab has
#         <DISK_FREE_THRESHOLD_PERCENT free disk space on either the moblab or
#         stateful partition.
#     """
#     partitions = [common.STATEFUL_MOUNTPOINT]
#     for part in partitions:
#       diskusage = self.diskinfo.DiskUsage(part)
#       free = 1 - diskusage.percent_used / 100.0
#       if free < common.DISK_FREE_THRESHOLD_PERCENT:
#         return DISK_SPACE_CODES.INSUFFICIENT_FREE_SPACE

#     return DISK_SPACE_CODES.OK

#   def Diagnose(self, errcode):
#     if DISK_SPACE_CODES.INSUFFICIENT_FREE_SPACE == errcode:
#       return ('Moblab has less than %s percent free disk space. Please'
#               ' add more USB storage or'
#               ' free space to ensure proper functioning of your'
#               ' moblab.' % int(common.DISK_FREE_THRESHOLD_PERCENT * 100),
#               [moblab_actions.ClearOldDbRecords(), moblab_actions.ClearLogs()])

#     return ('Unknown error reached with error code: %s' % errcode, [])
