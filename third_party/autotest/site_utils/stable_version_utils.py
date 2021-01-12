# Copyright 2014 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# This file contains utility functions to get and set stable versions for given
# boards.

import common
import logging
import django.core.exceptions
from client.common_lib import global_config
from frontend import setup_django_environment
from frontend.afe import models
from moblab_common.moblab_configuration_connector import (
    MoblabConfigurationRpcConnector,
)


# Name of the default board. For boards that don't have stable version
# explicitly set, version for the default board will be used.
DEFAULT = "DEFAULT"

# Type of metadata to store stable_version changes.
_STABLE_VERSION_TYPE = "stable_version"


def get_all():
    """Get stable versions of all boards.

    @return: A dictionary of boards and stable versions.
    """
    versions = dict(
        [(v.board, v.version) for v in models.StableVersion.objects.all()]
    )
    # Set default to the global config value of CROS.stable_cros_version if
    # there is no entry in afe_stable_versions table.
    if not versions:
        versions = {DEFAULT: get(DEFAULT)}
    return versions


def get(board=DEFAULT):
    """Get stable version for the given board.

    @param board: Currently ignored! Name of the board.

    @return: Stable build version configured by user in MoblabConfiguration
             service. If nothing was configured returns system default.
    """
    return MoblabConfigurationRpcConnector.get_stable_build_version_resolved()
