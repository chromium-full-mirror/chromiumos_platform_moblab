# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import os
import tempfile
import json
import docker

import common
from autotest_lib.client.bin import utils as common_utils
from autotest_lib.client.common_lib import error
from autotest_lib.client.common_lib.cros import dev_server
from autotest_lib.client.common_lib.cros import retry
from autotest_lib.server import utils as server_utils
from autotest_lib.site_utils.ssp_containers import constants

def get_container_info(container_path, **filters):
    """Get a collection of container information in the given container path.

    @param container_path: Path to look for containers.
    @param filters: Key value to filter the containers, e.g., name='base'

    @return: A list of dictionaries that each dictionary has the information of
             a container. The keys are defined in ATTRIBUTES.
    """
    client = docker.from_env(timeout=300)
    containers = client.containers.list(filters={"name": "^test_.*"})
    info_collection = []
    for container in containers:
          info = {"name": container.name, "state": container.status.upper()}
          info_collection.append(info)
    if filters:
        logging.info("filters %s", filters)
        filtered_collection = []
        for key, value in filters.iteritems():
            for info in info_collection:
                logging.info("key %s info %s value %s", key, info, value)
                if key in info and info[key] == value:
                    filtered_collection.append(info)
        info_collection = filtered_collection
    return info_collection


def download_extract(url, target, extract_dir, name):
    """Download the file from given url and save it to the target, then extract.

    @param url: Url to download the file.
    @param target: Path of the file to save to.
    @param extract_dir: Directory to extract the content of the file to.
    """
    remote_url = dev_server.DevServer.get_server_url(url)

    client = docker.from_env(timeout=300)
    container = client.containers.get(name)
    result = container.exec_run('curl %s -o %s' % (url, target))
    result = container.exec_run('tar xf %s -C %s' % (target, extract_dir))


# Make sure retries only happen in the non-timeout case.
@retry.retry((error.CmdError),
             blacklist=[error.CmdTimeoutError],
             timeout_min=3*2,
             delay_sec=10)
def _download_via_curl(url, target_file_path):
    # We do not want to retry on CmdTimeoutError but still retry on
    # CmdError. Hence we can't use curl --timeout=...
    common_utils.run('sudo curl -s %s -o %s' % (url, target_file_path),
                     stderr_tee=common_utils.TEE_TO_LOGS, timeout=3*60)


# Make sure retries only happen in the non-timeout case.
@retry.retry((error.CmdError),
             blacklist=[error.CmdTimeoutError],
             timeout_min=(constants.DEVSERVER_CALL_TIMEOUT *
                          constants.DEVSERVER_CALL_RETRY / 60),
             delay_sec=constants.DEVSERVER_CALL_DELAY)
def _download_via_devserver(url, target_file_path):
    dev_server.ImageServerBase.download_file(
            url, target_file_path, timeout=constants.DEVSERVER_CALL_TIMEOUT)

