# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Interface to the devserver server for all moblab code."""

import requests
import logging
import sys

DEV_SERVER = "devserver:8080"

_LOGGER = logging.getLogger('__name__')

class DevserverConnector(object):
    """Connector the the moblab devserver."""

    def __init__(self, moblab_cloud_storage):
        self.cloud_storage = moblab_cloud_storage

    def send_devserver_command(self, command, params):
        """Call the devserver with a command and params.

        This method should be considered private to this class.

        Args:
            command (string): Any available devserver command.
            params (string): URL encoded params.

        Returns:
            boolean: True if the command returned a 200 response code
                otherwise False.
        """

        url = "http://%s/%s?%s" % (DEV_SERVER, command, params)
        _LOGGER.info("Devserver request %s", url)
        try:
            response = requests.get(url, timeout=10 * 60)
        except requests.exceptions.RequestException as e:
            _LOGGER.error(e)
            return False
        _LOGGER.info(response)
        return response.status_code == 200

    def stage_build_on_devserver(self, archive_url, artifacts):
        """Request the devserver copy a build to its local cache.

        Args:
            archive_url (string): a full cloud location of a build.
            artifacts (string): a comma separated list of artifacts.

        Returns:
            boolean: True if the command returned succeeds.  Caching,
            can take some time so you have to call
            check_build_staged_on_devserver to ensure the build is
            actually in the cache.
        """

        command = "stage"
        params = "archive_url=%s&artifacts=%s" % (archive_url, artifacts)
        return self.send_devserver_command(command, params)

    def check_build_staged_on_devserver(self, archive_url, artifacts):
        """Check to see if this build is in the devserver cache.

        Args:
            archive_url (string): a full cloud location of a build.
            artifacts (string): a comma separated list of artifact.

        Returns:
            boolean: True if the build is in the cache.
        """

        command = "is_staged"
        params = "archive_url=%s&artifacts=%s" % (archive_url, artifacts)
        return self.send_devserver_command(command, params)

    def stage_build(self, board, build, build_type="release", archive_url=None):
        """Stage a build to the local moblab cache.

        By default the source of the build is the moblab's configured bucket,
        this can be overridden, allowing builds to be cached from other buckets
        or potentially a signed URL provided from CPCon to allow direct access
        to builds without copies to local buckets.

        Args:
            board (string): Software build to run, e.g. octopus
            build (string): Software version to run e.g. R73-11647.24.0
            build_type (str, optional): Defaults to 'release'. used to
                build the full build name octopus-release/R73-11647.24.0
            archive_url (string, optional): Defaults to None. A google cloud
                URI to a build to stage the moblab needs to be able to read the
                contents of that URI.

        Returns:
            boolean: True if the build is in the moblab cache, otherwise False.
        """

        artifacts = "full_payload,autotest_packages,stateful,quick_provision"
        if not archive_url:
            archive_url = "gs://%s/%s-%s/%s" % (
                self.cloud_storage,
                board,
                build_type,
                build,
            )

        if not self.check_build_staged_on_devserver(archive_url, artifacts):
            self.stage_build_on_devserver(archive_url, artifacts)
            logging.info("Staging: %s for board: %s" % (build, board))
            return self.check_build_staged_on_devserver(archive_url, artifacts)
        logging.info("Build already staged: %s for board: %s" % (build, board))
        return True
