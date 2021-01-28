# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This module provides some tools to interact with SSP containers, for example:
  1. Download base container from given GS location, setup the base container.
  2. Create a snapshot as test container from base container.
  3. Mount a directory in drone to the test container.
  4. Run a command in the container and return the output.
  5. Cleanup, e.g., destroy the container.
"""

from site_utils.ssp_containers.constants import *
from site_utils.ssp_containers.container import Container
from site_utils.ssp_containers.container import ContainerId
from site_utils.ssp_containers.container_bucket import ContainerBucket
from site_utils.ssp_containers.container_factory import ContainerFactory
from site_utils.ssp_containers.shared_host_dir import SharedHostDir
