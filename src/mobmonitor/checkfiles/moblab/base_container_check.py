# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""LXC base container checks."""

from __future__ import print_function

import common
import moblab_actions

from util import osutils
from util import config

class BASE_CONTAINER_CODES:
  OK = 0
  BASE_CONTAINER_MISSING = -1

class BaseContainerCheck(object):
  """Verifies that the base container exists."""

  CONTAINER_PATH = '/mnt/moblab/containers'

  def Check(self):
    """Verifies that moblab has a properly configured base lxc container

    Returns:
      BASE_CONTAINER_CODES
        OK if the base container is ok
        BASE_CONTAINER_MISSING if the container files are not present on moblab
    """
    container_base_name = config.Config().get('container_base_name')

    try:
      # Check that the base container is present at all in the filesystem
      check_container_path = '%s/%s' % (self.CONTAINER_PATH,
          container_base_name)
      check_container_rootfs = '%s/rootfs' % check_container_path
      osutils.run_command(['test', '-e', check_container_path])
      osutils.run_command(['test', '-e', check_container_rootfs])
    except osutils.RunCommandError:
      return BASE_CONTAINER_CODES.BASE_CONTAINER_MISSING

    return BASE_CONTAINER_CODES.OK


  def Diagnose(self, errcode):
    msg = ('Base lxc container is missing. This container is required to run'
            ' most tests. Please redownload and reinstall the base lxc'
            ' container (about 400MB)')
    if BASE_CONTAINER_CODES.BASE_CONTAINER_MISSING == errcode:
      return (msg, [moblab_actions.RepairBaseContainer()])
