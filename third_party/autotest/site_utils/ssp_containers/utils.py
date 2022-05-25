# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This module provides some utilities used by SSP_CONTAINER and its tools.
"""

import logging
import os
import re
import shutil
import tempfile
import unittest
from contextlib import contextmanager
import docker

import common
from client.bin import utils
from client.common_lib import error
from client.common_lib.cros.network import interface
from client.common_lib import global_config
from site_utils.ssp_containers import constants

def path_exists(container_name, path):
    """Check if path exists.

    If the process is not running with root user, os.path.exists may fail to
    check if a path owned by root user exists. This function uses command
    `test -e` to check if path exists.

    @param path: Path to check if it exists.

    @return: True if path exists, otherwise False.
    """
    client = docker.from_env(timeout=300)
    container = client.containers.get(container_name)
    logging.info('test -e "%s"', path)
    result = container.exec_run('test -e "%s"' % path, user='moblab')
    logging.info('test -e "%s" results %d', path, result.exit_code)
    return result.exit_code == 0



def get_host_ip():
    """Get the IP address of the host running containers

    @return: IP address of the host running containers.
    """
    return "autotest"

def is_vm():
    return False


def destroy(path, name,
            force=True, snapshots=False, ignore_status=False, timeout=-1):
  """
  Destroy an SSP_CONTAINER container.

  @param force: Destroy even if running. Default true.
  @param snapshots: Destroy all snapshots based on the container. Default false.
  @param ignore_status: Ignore return code of command. Default false.
  @param timeout: Seconds to wait for completion. No timeout imposed if the
    value is negative. Default -1 (no timeout).

  @returns: CmdResult object from the shell command
  """
  client = docker.from_env(timeout=300)
  container = client.containers.get(name)
  container.stop()
  return

def clone(ssp_container_path, src_name, new_path, dst_name, snapshot, hostname):
    """Clones a container.

    @param ssp_container_path: The SSP_CONTAINER path of the source container.
    @param src_name: The name of the source container.
    @param new_path: The SSP_CONTAINER path of the destination container.
    @param dst_name: The name of the destination container.
    @param snapshot: Whether or not to create a snapshot clone.
    """
    label = os.environ.get('LABEL', 'release')
    registry = os.environ.get('REGISTRY_URI', 'gcr.io/chromeos-partner-moblab')
    servod_label = os.environ.get('SERVOD_CONTAINER_LABEL', 'release')
    servod_registry = os.environ.get('SERVOD_REGISTRY_URI', 'us-docker.pkg.dev/chromeos-partner-moblab/common-core')
    client = docker.from_env(timeout=300)
    image = "%s/moblab-ssp:%s" % (registry, label)
    logging.info("Image %s", image)
    # At the start of every SSP container start we try to pull a new image
    # in case there is an update.
    # If there is a network outage in the middle of a suite run then the SSP
    # setup will fail, ignore failed pulls - if there is no image in the
    # local cache the run command will fail, otherwise just keep going with
    # the local version.
    try:
        client.images.pull(image)
    except docker.errors.APIError:
        logging.exception('Failed to pull image')

    client.containers.run(
        image,
        remove=True,
        name=dst_name,
        hostname=dst_name,
        network='default_moblab',
        cap_add=['ALL'],
        user='moblab',
        dns=['192.168.100.51'],
        detach=True,
        volumes={
            'default_results': {'bind': '/results', 'mode': 'rw'},
            'default_results': {'bind': '/usr/local/autotest/results', 'mode': 'rw'},
            'default_shadowconfig': {'bind': '/shadow_config', 'mode': 'ro'},
            '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
        },
        environment=[
            "MOBLAB=1",
            "LABEL=%s" % label,
            "REGISTRY_URI=%s" % servod_registry,
            "SERVOD_CONTAINER_LABEL=%s" % servod_label,
            "DOCKER_DEFAULT_NETWORK=default_moblab"
        ]

    )

@contextmanager
def TempDir(*args, **kwargs):
    """Context manager for creating a temporary directory."""
    tmpdir = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)


class BindMount(object):
    """Manages setup and cleanup of bind-mounts."""
    def __init__(self, spec):
        """Sets up a new bind mount.

        Do not call this directly, use the create or from_existing class
        methods.

        @param spec: A two-element tuple (dir, mountpoint) where dir is the
                     location of an existing directory, and mountpoint is the
                     path under that directory to the desired mount point.
        """
        self.spec = spec


    def __eq__(self, rhs):
        if isinstance(rhs, self.__class__):
            return self.spec == rhs.spec
        return NotImplemented


    def __ne__(self, rhs):
        return not (self == rhs)


    @classmethod
    def create(cls, src, dst, rename=None, readonly=False):
        """Creates a new bind mount.

        @param src: The path of the source file/dir.
        @param dst: The destination directory.  The new mount point will be
                    ${dst}/${src} unless renamed.  If the mount point does not
                    already exist, it will be created.
        @param rename: An optional path to rename the mount.  If provided, the
                       mount point will be ${dst}/${rename} instead of
                       ${dst}/${src}.
        @param readonly: If True, the mount will be read-only.  False by
                         default.

        @return An object representing the bind-mount, which can be used to
                clean it up later.
        """
        spec = (dst, (rename if rename else src).lstrip(os.path.sep))
        full_dst = os.path.join(*list(spec))

        if not path_exists(full_dst):
            utils.run('mkdir -p %s' % full_dst)

        utils.run('mount --bind %s %s' % (src, full_dst))
        if readonly:
            utils.run('mount -o remount,ro,bind %s' % full_dst)

        return cls(spec)


    @classmethod
    def from_existing(cls, host_dir, mount_point):
        """Creates a BindMount for an existing mount point.

        @param host_dir: Path of the host dir hosting the bind-mount.
        @param mount_point: Full path to the mount point (including the host
                            dir).

        @return An object representing the bind-mount, which can be used to
                clean it up later.
        """
        spec = (host_dir, os.path.relpath(mount_point, host_dir))
        return cls(spec)


    def cleanup(self):
        """Cleans up the bind-mount.

        Unmounts the destination, and deletes it if possible. If it was mounted
        alongside important files, it will not be deleted.
        """
        full_dst = os.path.join(*list(self.spec))
        utils.run('umount %s' % full_dst)
        # Ignore errors because bind mount locations are sometimes nested
        # alongside actual file content (e.g. SSPs install into
        # /usr/local/autotest so rmdir -p will fail for any mounts located in
        # /usr/local/autotest).
        utils.run('bash -c "cd %s; rmdir -p --ignore-fail-on-non-empty %s"'
                  % self.spec)


def is_subdir(parent, subdir):
    """Determines whether the given subdir exists under the given parent dir.

    @param parent: The parent directory.
    @param subdir: The subdirectory.

    @return True if the subdir exists under the parent dir, False otherwise.
    """
    # Append a trailing path separator because commonprefix basically just
    # performs a prefix string comparison.
    parent = os.path.join(parent, '')
    return os.path.commonprefix([parent, subdir]) == parent


def sudo_commands(container_name, commands):
    """Takes a list of bash commands and executes them all with one invocation
    of . Saves ~400 ms per command.

    @param commands: The bash commands, as strings.

    @return The return code of the  call.
    """
    client = docker.from_env(timeout=300)
    container = client.containers.get(container_name)
    for command in commands:
        logging.info('Running command %s', command)
        container.exec_run(command, user='moblab')


