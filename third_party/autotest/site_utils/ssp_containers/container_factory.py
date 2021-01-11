# Copyright 2017 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging

import common
from client.bin import utils
from client.common_lib import error
from site_utils.ssp_containers import constants
from site_utils.ssp_containers import container



class ContainerFactory(object):
    """A factory class for creating SSP_CONTAINER container objects."""

    def __init__(self,
                 base_container,
                 container_class=container.Container,
                 snapshot=True,
                 force_cleanup=False,
                 ssp_container_path=constants.DEFAULT_CONTAINER_PATH):
        """Initializes a ContainerFactory.

        @param base_container: The base container from which other containers
                               are cloned.
        @param container_class: (optional) The Container class to instantiate.
                                By default, ssp_containers.Container is instantiated.
        @param snapshot: (optional) If True, creates SSP_CONTAINER snapshot clones instead
                         of full clones.  By default, snapshot clones are used.
        @param force_cleanup: (optional) If True, if a container is created with
                              a name and SSP_CONTAINER directory matching an existing
                              container, the existing container is destroyed,
                              and the new container created in its place. By
                              default, existing containers are not destroyed and
                              a ContainerError is raised.
        @param ssp_container_path: (optional) The default SSP_CONTAINER path that will be used for
                         new containers.  If one is not provided, the
                         DEFAULT_CONTAINER_PATH from ssp_containers.constants will be used.
                         Note that even if a path is provided here, it can still
                         be overridden when create_container is called.
        """
        self._container_class = container_class
        self._base_container = base_container
        self._snapshot = snapshot
        self._force_cleanup = force_cleanup
        self._ssp_container_path = ssp_container_path

    def create_container(self, cid=None, hostname=None, ssp_container_path=None):
        """Creates a new container.

        @param cid: (optional) A ContainerId for the new container.  If an ID is
                    provided, it determines both the name and the ID of the
                    container.  If no ID is provided, a random name is generated
                    for the container, and it is not assigned an ID.
        @param ssp_container_path: (optional) The SSP_CONTAINER path for the new container.  If one
                         is not provided, the factory's default ssp_container_path
                         (specified when the factory was constructed) is used.
        """
        name = str(cid) if cid else None
        if ssp_container_path is None:
            ssp_container_path = self._ssp_container_path

        logging.info('Creating new container (name: %s, ssp_container_path: %s)', name,
                     ssp_container_path)

        # If an ID is provided, use it as the container name.
        new_container = self._create_from_base(name, ssp_container_path, hostname)
        # If an ID is provided, assign it to the container.  When the container
        # is created just-in-time by the container bucket, this ensures that the
        # resulting container is correctly registered with the autoserv system.
        # If the container is being created by a container pool, the ID will be
        # assigned later, when the continer is bound to an actual test process.
        if cid:
            new_container.id = cid
        return new_container

    def _create_from_base(self, name, ssp_container_path, hostname):
        """Creates a container from the base container.

        @param name: Name of the container.
        @param ssp_container_path: The SSP_CONTAINER path of the new container.

        @return: A Container object for the created container.

        @raise ContainerError: If the container already exist.
        """
        use_snapshot = False

        return self._container_class.clone(
            src=self._base_container,
            new_name=name,
            new_path=ssp_container_path,
            snapshot=use_snapshot,
            cleanup=self._force_cleanup,
            hostname=hostname)

