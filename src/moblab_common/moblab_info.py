# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Utilities to return information about the current moblab."""

# pylint: disable=cros-logging-import
import logging
import uuid

from moblab_common import lock_util
from moblab_common import host_connector

MOBLAB_USER = "moblab"
MOBLAB_GROUP = "moblab"
MOBLAB_ID_FILENAME = "/home/moblab/.moblab_id"
_ID_FILE_LOCK_PATH = "%s.lock" % MOBLAB_ID_FILENAME

# TODO(guocb): Remove get_moblab_id() and get_moblab_serialnumber() completely
# from autotest code base.


def get_or_create_id():
    """Gets the moblab random id and write it to id file if necessary.

    The random id file is cached on disk. If it does not exist, a new file is
    created the first time.

    Returns:
        The moblab random id.
    """
    try:
        with open(MOBLAB_ID_FILENAME) as id_file:
            random_id = id_file.read()
    except IOError:
        with lock_util.file_lock(_ID_FILE_LOCK_PATH, exclusive=True, timeout_seconds=1):
            # Check again to see if another process just created it.
            try:
                with open(MOBLAB_ID_FILENAME) as id_file:
                    return id_file.read()
            except IOError:
                pass

            random_id = uuid.uuid1().hex
            with open(MOBLAB_ID_FILENAME, "w") as id_file:
                id_file.write(random_id)

    return random_id


_VPD_KEY_SERIAL_NUMBER = "serial_number"
_VPD_KEY_ETH_MAC = "ethernet_mac"
NO_SERIAL_NUMBER = "NoSerialNumber"


def get_serial_number():
    """Gets a unique identifier for the moblab.

    """
    try:
        return host_connector.HostServicesConnector.get_host_identifier()
    except host_connector.HostServicesException:
        logging.exception("Failed to get serial number from host.")
    return NO_SERIAL_NUMBER
