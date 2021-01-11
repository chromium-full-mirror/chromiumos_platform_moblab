# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import json
import logging
import os
import re
import tempfile
import time
import tempfile
import tarfile

import docker

import common
from client.bin import utils
from client.common_lib import error
from site_utils.ssp_containers import constants
from site_utils.ssp_containers import ssp_containers
from site_utils.ssp_containers import utils as ssp_container_utils


# Naming convention of test container, e.g., test_300_1422862512_2424, where:
# 300:        The test job ID.
# 1422862512: The tick when container is created.
# 2424:       The PID of autoserv that starts the container.
_TEST_CONTAINER_NAME_FMT = 'test_%s_%d_%d'
# Name of the container ID file.
_CONTAINER_ID_FILENAME = 'container_id.json'


class ContainerId(collections.namedtuple('ContainerId',
                                         ['job_id', 'creation_time', 'pid'])):
    """An identifier for containers."""

    # Optimization.  Avoids __dict__ creation.  Empty because this subclass has
    # no instance vars of its own.
    __slots__ = ()


    def __str__(self):
        return _TEST_CONTAINER_NAME_FMT % self


    def save(self, path):
        """Saves the ID to the given path.

        @param path: Path to a directory where the container ID will be
                     serialized.
        """
        dst = os.path.join(path, _CONTAINER_ID_FILENAME)
        with open(dst, 'w') as f:
            json.dump(self, f)

    @classmethod
    def load(cls, path):
        """Reads the ID from the given path.

        @param path: Path to check for a serialized container ID.

        @return: A container ID if one is found on the given path, or None
                 otherwise.

        @raise ValueError: If a JSON load error occurred.
        @raise TypeError: If the file was valid JSON but didn't contain a valid
                          ContainerId.
        """
        src = os.path.join(path, _CONTAINER_ID_FILENAME)

        try:
            with open(src, 'r') as f:
                job_id, ctime, pid = json.load(f)
        except IOError:
            # File not found, or couldn't be opened for some other reason.
            # Treat all these cases as no ID.
            return None
        # TODO(pprabhu, crbug.com/842343) Remove this once all persistent
        # container ids have migrated to str.
        job_id = str(job_id)
        return cls(job_id, ctime, pid)


    @classmethod
    def create(cls, job_id, ctime=None, pid=None):
        """Creates a new container ID.

        @param job_id: The first field in the ID.
        @param ctime: The second field in the ID.  Optional. If not provided,
                      the current epoch timestamp is used.
        @param pid: The third field in the ID.  Optional.  If not provided, the
                    PID of the current process is used.
        """
        if ctime is None:
            ctime = int(time.time())
        if pid is None:
            pid = os.getpid()
        # TODO(pprabhu) Drop str() cast once
        # job_directories.get_job_id_or_task_id() starts returning str directly.
        return cls(str(job_id), ctime, pid)


class Container(object):
    """A wrapper class of an SSP_CONTAINER container.

    The wrapper class provides methods to interact with a container, e.g.,
    start, stop, destroy, run a command. It also has attributes of the
    container, including:
    name: Name of the container.
    state: State of the container, e.g., ABORTING, RUNNING, STARTING, STOPPED,
           or STOPPING.
    """

    def __init__(self, container_path, name, attribute_values, src=None,
                 snapshot=False, hostname=""):
        """Initialize an object of SSP_CONTAINER container with given attribute values.

        @param container_path: Directory that stores the container.
        @param name: Name of the container.
        @param attribute_values: A dictionary of attribute values for the
                                 container.
        @param src: An optional source container.  If provided, the source
                    continer is cloned, and the new container will point to the
                    clone.
        @param snapshot: If a source container was specified, this argument
                         specifies whether or not to create a snapshot clone.
                         The default is to attempt to create a snapshot.
                         If a snapshot is requested and creating the snapshot
                         fails, a full clone will be attempted.
        """
        # The container calls the docker API to run autoserv (the test) in
        # the container, so the call has to not timeout at least as long as
        # a single test might run.  Set to 14 days.
        # TODO -pass the timeout for the test along to the container so
        # it can timeout when the test timesout.
        self._client = docker.from_env(timeout=60*60*24*14)
        self._rootfs = None
        self.name = name
        self._id = self.name
        for attribute, value in attribute_values.iteritems():
            setattr(self, attribute, value)
        exists = ssp_containers.get_container_info(container_path, name=name)
        # Clone the source container to initialize this one.
        ssp_container_utils.clone("", "", container_path, name, snapshot, hostname)



    @classmethod
    def create_from_existing_dir(cls, ssp_container_path, name, **kwargs):
        """Creates a new container instance for an container that already
        exists on disk.

        @param ssp_container_path: The SSP_CONTAINER path for the container.
        @param name: The container name.

        @raise error.ContainerError: If the container doesn't already exist.

        @return: The new container.
        """
        return cls(ssp_container_path, name, kwargs)


    # Containers have a name and an ID.  The name is simply the name of the SSP_CONTAINER
    # container.  The ID is the actual key that is used to identify the
    # container to the autoserv system.  In the case of a JIT-created container,
    # we have the ID at the container's creation time so we use that to name the
    # container.  This may not be the case for other types of containers.
    @classmethod
    def clone(cls, src, new_name, new_path=None, snapshot=False,
              cleanup=False, hostname=""):
        """Creates a clone of this container.

        @param src: The original container.
        @param new_name: Name for the cloned container.  If this is not
                         provided, a random unique container name will be
                         generated.
        @param new_path: SSP_CONTAINER path for the cloned container (optional; if not
                         specified, the new container is created in the same
                         directory as the source container).
        @param snapshot: Whether to snapshot, or create a full clone.  Note that
                         snapshot cloning is not supported on all platforms.  If
                         this code is running on a platform that does not
                         support snapshot clones, this flag is ignored.
        @param cleanup: If a container with the given name and path already
                        exist, clean it up first.
        """
        if new_path is None:
            new_path = src.container_path

        if new_name is None:
            _, new_name = os.path.split(
                tempfile.mkdtemp(dir=new_path, prefix='container.'))
            logging.debug('Generating new name for container: %s', new_name)
        else:
            # If a container exists at this location, clean it up first
            pass
        # Create and return the new container.
        new_container = cls(new_path, new_name, {}, src, snapshot, hostname)
        return new_container


    def refresh_status(self):
        """Refresh the status information of the container.
        """
        containers = ssp_containers.get_container_info("", name=self.name)
        if not containers:
            raise error.ContainerError(
                    'No container found in directory %s with name of %s.' %
                    (self.container_path, self.name))
        attribute_values = containers[0]
        for attribute, value in attribute_values.iteritems():
            setattr(self, attribute, value)

    def attach_run(self, command, bash=True, user='moblab'):
        """Attach to a given container and run the given command.

        @param command: Command to run in the container.
        @param bash: Run the command through bash -c "command". This allows
                     pipes to be used in command. Default is set to True.

        @return: The output of the command.

        @raise error.CmdError: If container does not exist, or not running.
        """
        #raise Exception(command)
        logging.info("Running %s", command)
        container = self._client.containers.get(self.name)
        result = container.exec_run(command, user=user)
        logging.info("Result %d %s", result.exit_code, result.output)
        return utils.CmdResult(command, result.output, "", result.exit_code)


    def is_network_up(self):
        """Check if network is up in the container by curl base container url.

        @return: True if the network is up, otherwise False.
        """
        return True



    def start(self, wait_for_network=True):
        """Start the container.

        @param wait_for_network: True to wait for network to be up. Default is
                                 set to True.

        @raise ContainerError: If container does not exist, or fails to start.
        """
        pass


    def stop(self):
        """Stop the container.

        @raise ContainerError: If container does not exist, or fails to start.
        """
        container = self._client.containers.get(self.name)
        container.stop()


    def destroy(self, force=True):
        """Destroy the container.

        @param force: Set to True to force to destroy the container even if it's
                      running. This is faster than stop a container first then
                      try to destroy it. Default is set to True.

        @raise ContainerError: If container does not exist or failed to destroy
                               the container.
        """
        logging.debug('Destroying container %s/%s',
                      "",
                      self.name)
        ssp_container_utils.destroy("", self.name, force=force)


    def mount_dir(self, source, destination, readonly=False):
        """Mount a directory in host to a directory in the container.

        @param source: Directory in host to be mounted.
        @param destination: Directory in container to mount the source directory
        @param readonly: Set to True to make a readonly mount, default is False.
        """
        pass
    def verify_autotest_setup(self, job_folder):
        """Verify autotest code is set up properly in the container.

        @param job_folder: Name of the job result folder.

        @raise ContainerError: If autotest code is not set up properly.
        """
        # Test autotest code is setup by verifying a list of
        # (directory, minimum file count)
        directories_to_check = [
                (constants.CONTAINER_AUTOTEST_DIR, 3),
                (constants.CONTAINER_SITE_PACKAGES_PATH, 3)]
        for directory, count in directories_to_check:
            cmd = (constants.COUNT_FILE_CMD % {'dir': directory})
            result = self.attach_run('bash -c "%s"' % cmd)
            file_count = int(result.stdout)
            logging.debug('%s entries in %s.', count, directory)
            if file_count < count:
                raise error.ContainerError('%s is not properly set up.' %
                                           directory)
        self.attach_run('test -f /root/gsutil/gsutil && '
                        'ln -s /root/gsutil/gsutil /usr/bin/gsutil || true')


    def modify_import_order(self):
        """Swap the python import order of lib and local/lib.

        In Moblab, the host's python modules located in
        /usr/lib64/python2.7/site-packages is mounted to following folder inside
        container: /usr/local/lib/python2.7/dist-packages/. The modules include
        an old version of requests module, which is used in autotest
        site-packages. For test, the module is only used in
        dev_server/symbolicate_dump for requests.call and requests.codes.OK.
        When pip is installed inside the container, it installs requests module
        with version of 2.2.1 in /usr/lib/python2.7/dist-packages/. The version
        is newer than the one used in autotest site-packages, but not the latest
        either.
        According to /usr/lib/python2.7/site.py, modules in /usr/local/lib are
        imported before the ones in /usr/lib. That leads to pip to use the older
        version of requests (0.11.2), and it will fail. On the other hand,
        requests module 2.2.1 can't be installed in CrOS (refer to CL:265759),
        and higher version of requests module can't work with pip.
        The only fix to resolve this is to switch the import order, so modules
        in /usr/lib can be imported before /usr/local/lib.
        """
        site_module = '/usr/lib/python2.7/site.py'
        self.attach_run(" sed -i ':a;N;$!ba;s/\"local\/lib\",\\n/"
                        "\"lib_placeholder\",\\n/g' %s" % site_module)
        self.attach_run(" sed -i ':a;N;$!ba;s/\"lib\",\\n/"
                        "\"local\/lib\",\\n/g' %s" % site_module)
        self.attach_run(' sed -i "s/lib_placeholder/lib/g" %s' %
                        site_module)
        pass


    def is_running(self):
        """Returns whether or not this container is currently running."""
        self.refresh_status()
        return self.state == 'RUNNING'


    def set_hostname(self, hostname):
        """Sets the hostname within the container.

        This method can only be called on a running container.

        @param hostname The new container hostname.

        @raise ContainerError: If the container is not running.
        """
        if not self.is_running():
            raise error.ContainerError(
                    'set_hostname can only be called on running containers.')

        self.attach_run('hostname %s' % (hostname))
        self.attach_run(constants.APPEND_CMD_FMT % {
                'content': '127.0.0.1 %s' % (hostname),
                'file': '/etc/hosts'})


    def install_ssp(self, ssp_url):
        """Downloads and installs the given server package.

        @param ssp_url: The URL of the ssp to download and install.
        """
        usr_local_path = os.path.join('/usr', 'local')
        autotest_pkg_path = os.path.join(usr_local_path,
                                         'autotest_server_package.tar.bz2')
        self.attach_run('mkdir -p %s' % usr_local_path)
        self.attach_run('chown -R moblab:moblab %s' % usr_local_path + '/autotest', user='root')

        ssp_containers.download_extract(ssp_url, autotest_pkg_path, usr_local_path, self.name)


    def install_control_file(self, control_file):
        """Installs the given control file.

        The given file will be copied into the container.

        @param control_file: Path to the control file to install.
        """
        dst = os.path.join(constants.CONTROL_TEMP_PATH,
                           os.path.basename(control_file))
        self.copy(control_file, dst)


    def copy(self, host_path, container_path):
        """Copies files into the container.

        @param host_path: Path to the source file/dir to be copied.
        @param container_path: Path to the destination dir (in the container).
        """
        self._do_copy(src=host_path, dst=container_path)


    @property
    def id(self):
        """Returns the container ID."""
        return self._id


    @id.setter
    def id(self, new_id):
        """Sets the container ID."""
        self._id = new_id;
        # Persist the ID so other container objects can pick it up.
        #self._id.save(os.path.join(self.container_path, self.name))

    def simple_tar(self, path):
        f = tempfile.NamedTemporaryFile()
        t = tarfile.open(mode='w', fileobj=f)

        abs_path = os.path.abspath(path)
        t.add(abs_path, arcname=os.path.basename(path), recursive=True)

        t.close()
        f.seek(0)
        return f

    def _do_copy(self, src, dst):
        """Copies files and directories on the host system.

        @param src: The source file or directory.
        @param dst: The destination file or directory.  If the path to the
                    destination does not exist, it will be created.
        """
        # Create the dst dir. mkdir -p will not fail if dst_dir exists.
        dst_dir = os.path.dirname(dst)
        #self.attach_run('mkdir -p %s' % dst_dir)
        logging.info("Do copy %s %s" % (src, dst))
        self.attach_run('ls %s' % dst_dir, user='root')
        container = self._client.containers.get(self.name)
        container.put_archive(dst_dir, self.simple_tar(src))

    def _set_ssp_container_config(self, key, value):
        """Sets an SSP_CONTAINER config value for this container.

        Configuration changes made while a container is running don't take
        effect until the container is restarted.  Since this isn't a scenario
        that should ever come up in our use cases, calling this method on a
        running container will cause a ContainerError.

        @param key: The SSP_CONTAINER config key to set.
        @param value: The value to use for the given key.

        @raise error.ContainerError: If the container is already started.
        """
        pass


    def _get_ssp_container_config(self, key):
        """Retrieves an SSP_CONTAINER config value from the container.

        @param key The key of the config value to retrieve.
        """
        pass
