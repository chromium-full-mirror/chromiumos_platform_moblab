#!/usr/bin/python
#
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import os
import re
import time

import common

from autotest_lib.site_utils.lxc import container_bucket
from autotest_lib.site_utils import lxc

CONTAINER_POOL_IP_START = 176
CONTAINER_POOL_IP_END = 250


class SSPContainerTestException(Exception):
  pass

def create_delete_container(job_id):
  cb = container_bucket.ContainerBucket()
  container_id = lxc.ContainerId(job_id, time.time(), os.getpid())
  container = cb._factory.create_container(container_id)
  container.start(wait_for_network=True)
  ifconfig = container.attach_run("ifconfig eth0").stdout
  match = re.search(
      r".*inet addr:([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\.([0-9]{1,3}).*",
      ifconfig)
  if not match:
    logging.error(ifconfig)
    raise SSPContainerTestException(
        "Test fail, unable to determine the container IP address")
  last_ip_digits = int(match.group(2))
  if (last_ip_digits < CONTAINER_POOL_IP_START or
      last_ip_digits > CONTAINER_POOL_IP_END):
    raise SSPContainerTestException(
        "Test fail, the container IP address is not in the correct range %s.%s"
        % (match.group(1), match.group(2)))
  container.destroy()
  return last_ip_digits


if __name__ == "__main__":
  # This is specifically 1 more than the range to ensure we wrap IP address
  container_ips = []
  number_of_containers_to_test = (CONTAINER_POOL_IP_END -
                                  CONTAINER_POOL_IP_START + 1)

  #TODO(haddowk) run 20 in parrallel to emulate a typically DUT load.
  for i in range(0, number_of_containers_to_test):
    container_ips.append(create_delete_container(i))

  if len(container_ips) < number_of_containers_to_test:
    raise SSPContainerTestException("Not all IP's tested")

  logging.info("SSP Container tests pass")
