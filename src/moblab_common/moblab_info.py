# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Utilities to return information about the current moblab."""

import logging
import uuid
import docker

from moblab_common import lock_util
from moblab_common import host_connector
from moblab_common.utils.constants import Constants as MoblabConstants

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MOBLAB_USER = "moblab"
MOBLAB_GROUP = "moblab"
MOBLAB_ID_FILENAME = "/home/moblab/.moblab_id"
_ID_FILE_LOCK_PATH = "%s.lock" % MOBLAB_ID_FILENAME

# TODO(guocb): Remove get_moblab_id() and get_moblab_serialnumber() completely
# from autotest code base.


class MoblabInfoError(Exception):
    pass


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
        with lock_util.file_lock(
            _ID_FILE_LOCK_PATH, exclusive=True, timeout_seconds=1
        ):
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
    """Gets a unique identifier for the moblab."""
    try:
        return host_connector.HostServicesConnector.get_host_identifier()
    except host_connector.HostServicesException:
        _LOGGER.exception("Failed to get serial number from host.")
    return NO_SERIAL_NUMBER


def _get_public_ip_address():
    """
        Gets the public IP address.

    Returns:
        public ip address as string.
    """
    try:
        return host_connector.HostServicesConnector.get_ip()
    except host_connector.HostServicesException:
        _LOGGER.exception("Failed to get ip address from host.")
        return None


def get_network_info():
    """
        Gets network info of Moblab.

        TCP socket is used to test the connectivity. If there is no
        connectivity, try to get the public IP with UDP socket.

    Returns:
        A dict of network information ( specifically, a 'server_ip' and
        'is_connected' which is true iff Moblab is connected to internet.
    """
    ip = _get_public_ip_address()
    if ip is None or ip == "localhost":
        return {"server_ip": None, "is_connected": False}
    else:
        _LOGGER.info("Established TCP connection with well known server.")
        return {"server_ip": ip, "is_connected": True}


def get_version_info():
    """
        Gets cloud version info of Moblab.
    Returns:
        A dict of ChromeOS and Moblab information (ex. serial number,
        release version )
    """
    version_info = {}
    version_info[MoblabConstants.MOBLAB_INSTALL_ID_NAME] = get_or_create_id()
    version_info[MoblabConstants.MOBLAB_HOST_ID_NAME] = get_serial_number()

    version_info[MoblabConstants.MOBLAB_RELEASE_VERSION] = _get_moblab_version()

    host_version_info = None
    try:
        host_version_info = (
            host_connector.HostServicesConnector.get_system_version()
        )
    except host_connector.HostServicesException:
        msg = "Failed to get version information from host."
        _LOGGER.exception(msg)
        raise MoblabInfoError(msg)

    version_info[
        MoblabConstants.BUILD_VERSION_NAME
    ] = host_version_info.version

    version_info[
        MoblabConstants.DESCRIPTION_NAME
    ] = host_version_info.description

    version_info[MoblabConstants.CHANNEL_NAME] = host_version_info.track

    _LOGGER.info(version_info)
    return version_info

def _get_moblab_version():
    """
        Get the name a version label from compose container.

        At build time a version string is embedded into the image as a label,
        retrieve those numbers.

    Returns:
        The value of the version label of compose container.
    """
    client = docker.from_env(timeout=300)
    try:
        container = client.containers.get(
            # this has to be compose, but temporarily we look at rpc container
            MoblabConstants.MOBLAB_RPC_SERVER_CONTAINER_NAME
        )
        version = container.labels.get("version", "autopush")
    except docker.errors.NotFound:
        _LOGGER.exception("Compose container was not found.")
        return "no version found"
    return version
