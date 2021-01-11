# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Utility functions for AFE-based interactions.

NOTE: This module should only be used in the context of a running test. Any
      utilities that require accessing the AFE, should do so by creating
      their own instance of the AFE client and interact with it directly.
"""

import common
import logging
import traceback
import urlparse

from client.common_lib import global_config
from server.cros import autoupdater
from server.cros import provision
from server.cros.dynamic_suite import frontend_wrappers
#from site_utils import stable_version_classify as sv
from server import site_utils as server_utils
from server.cros.dynamic_suite import constants as ds_constants
from server.cros.dynamic_suite import tools
from server.cros.dynamic_suite import frontend_wrappers

from chromite.lib import auto_updater
from chromite.lib import remote_access


# TODO(crbug.com/1058095) -- the autotest frontend has been turned down
# reduce the timeouts so that we spend less time failing to contact it.
AFE = frontend_wrappers.RetryingAFE(timeout_min=(1.0/60), delay_sec=1)
_CROS_VERSION_MAP = AFE.get_stable_version_map(AFE.CROS_IMAGE_TYPE)
_FIRMWARE_VERSION_MAP = AFE.get_stable_version_map(AFE.FIRMWARE_IMAGE_TYPE)
_FAFT_VERSION_MAP = AFE.get_stable_version_map(AFE.FAFT_IMAGE_TYPE)

_CONFIG = global_config.global_config
ENABLE_DEVSERVER_TRIGGER_AUTO_UPDATE = _CONFIG.get_config_value(
        'CROS', 'enable_devserver_trigger_auto_update', type=bool,
        default=False)
AFE = frontend_wrappers.RetryingAFE(timeout_min=(1.0/60), delay_sec=1)
_CROS_VERSION_MAP = AFE.get_stable_version_map(AFE.CROS_IMAGE_TYPE)

DEVICE_BASE_DIR = '/usr/local/tmp/au-provision'

def _host_in_lab(host):
    """Check if the host is in the lab and an object the AFE knows.

    This check ensures that autoserv and the host's current job is running
    inside a fully Autotest instance, aka a lab environment. If this is the
    case it then verifies the host is registed with the configured AFE
    instance.

    @param host: Host object to verify.

    @returns The host model object.
    """
    if not host.job or not host.job.in_lab:
        return False
    return host._afe_host


def _log_image_name(image_name):
    try:
        logging.debug("_log_image_name: image (%s)", image_name)
        server_utils.ParseBuildName(name=image_name)
    except Exception:
        logging.error(traceback.format_exc())


def _format_image_name(board, version):
    return "%s-release/%s" % (board, version)


def get_stable_cros_image_name_v2(info, _config_override=None):
    if sv.classify_board(info.board, _config_override=_config_override) == sv.FROM_HOST_CONFIG:
        logging.debug("get_stable_cros_image_name_v2: board %s from host_info_store" % info.board)
        out = _format_image_name(board=info.board, version=info.cros_stable_version)
        _log_image_name(out)
        return out
    logging.debug("get_stable_cros_image_name_v2: board %s from autotest frontend" % info.board)
    return get_stable_cros_image_name(info.board)


def get_stable_cros_image_name(board):
    """Retrieve the Chrome OS stable image name for a given board.

    @param board: Board to lookup.

    @returns Name of a Chrome OS image to be installed in order to
            repair the given board.
    """
    return _CROS_VERSION_MAP.get_image_name(board)



def get_stable_firmware_version_v2(host_info):
    """Retrieve the stable firmware version for a given model.

    @param host_info: a host_info_store object.

    @returns A version of firmware to be installed via
             `chromeos-firmwareupdate` from a repair build.
    """
    logging.debug("Get firmware stable_version for model: %s",
                  getattr(host_info, "model", None))
    return host_info.firmware_stable_version


def get_stable_faft_version_v2(host_info):
    """Retrieve the stable firmware version for FAFT DUTs.

    @param host_info: a host_info_store object.

    @returns A version of firmware to be installed in order to
            repair firmware on a DUT used for FAFT testing.
    """
    logging.debug("Get faft stable_version for model: %s",
                  getattr(host_info, "model", None))
    return host_info.faft_stable_version


def clean_provision_labels(host):
    """Clean provision-related labels.

    @param host: Host object.
    """
    info = host.host_info_store.get()
    info.clear_version_labels()
    attributes = host.get_attributes_to_clear_before_provision()
    for key in attributes:
      info.attributes.pop(key, None)

    host.host_info_store.commit(info)


def add_provision_labels(host, version_prefix, image_name,
                         provision_attributes={}):
    """Add provision labels for host.

    @param host: Host object.
    @param version_prefix: a string version prefix, e.g. "cros-version:"
    @param image_name: a string image name, e.g. peppy-release/R70-11011.0.0.
    @param provision_attributes: a map, including attributes for provisioning,
        e.g. {"job_repo_url": "http://..."}
    """
    info = host.host_info_store.get()
    info.attributes.update(provision_attributes)
    info.set_version_label(version_prefix, image_name)
    host.host_info_store.commit(info)


def machine_install_and_update_labels(host, update_url, with_cheets=False,
                                      staging_server=None):
    """Install a build and update the version labels on a host.

    @param host: Host object where the build is to be installed.
    @param update_url: URL of the build to install.
    @param with_cheets: If true, installation is for a specific, custom
        version of Android for a target running ARC.
    @param staging_server: Server where images have been staged. Typically,
        an instance of dev_server.ImageServer.
    """
    clean_provision_labels(host)

    logging.debug('Attempting to provision with autoupdater quick-provision.')
    updater = autoupdater.ChromiumOSUpdater(update_url, host=host)
    image_name, host_attributes = updater.run_update()

    if with_cheets:
        image_name += provision.CHEETS_SUFFIX
    add_provision_labels(host, host.VERSION_PREFIX, image_name, host_attributes)
