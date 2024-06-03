# Lint as: python2, python3
# Copyright (c) 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Expects to be run in an environment with  and no interactive password
# prompt, such as within the Chromium OS development chroot.


"""This is a base host class for servohost and labstation."""


import logging
import socket
import time
import os


from client.bin import utils
from client.common_lib import autotest_enum
from client.common_lib import error
from client.common_lib import hosts
from client.common_lib import lsbrelease_utils
from client.common_lib.cros import dev_server
from client.common_lib.cros import kernel_utils
from client.cros import constants as client_constants
from server import autotest
from server import site_utils as server_utils
from server.cros import provisioner
from server.hosts import ssh_host

import docker

#from site_utils.rpm_control_system import rpm_client


class BaseServoHost(ssh_host.SSHHost):
    """Base host class for a host that manage servo(s).
     E.g. beaglebone, labstation.
    """
    REBOOT_CMD = 'sleep 5; reboot & sleep 10; reboot -f'

    TEMP_FILE_DIR = '/var/lib/servod/'

    LOCK_FILE_POSTFIX = '_in_use'
    REBOOT_FILE_POSTFIX = '_reboot'

    # Time to wait a rebooting servohost, in seconds.
    REBOOT_TIMEOUT = 240

    # Timeout value to power cycle a servohost, in seconds.
    BOOT_TIMEOUT = 240

    # Constants that reflect current host update state.
    UPDATE_STATE = autotest_enum.AutotestEnum('IDLE', 'RUNNING',
                                              'PENDING_REBOOT')

    def _initialize(self,
                    hostname,
                    is_in_lab=None,
                    servo_host_ssh_port=None,
                    *args,
                    **dargs):
        """Construct a BaseServoHost object.

        @param is_in_lab: True if the servo host is in Cros Lab. Default is set
                          to None, for which utils.host_is_in_lab_zone will be
                          called to check if the servo host is in Cros lab.

        """

        super(BaseServoHost, self)._initialize(
            hostname=hostname, *args, **dargs
        )

        self._is_containerized_servod = True
        self._is_localhost = False

        self._is_in_lab = False

        self._sudo_required = False

        self._dut_host_info = None
        self._dut_hostname = None


    def get_board(self):
        """Determine the board for this servo host. E.g. fizz-labstation

        @returns a string representing this labstation's board or None if
         target host is not using a ChromeOS image(e.g. test in chroot).
        """
        output = self.run('cat /etc/lsb-release', ignore_status=True).stdout
        return lsbrelease_utils.get_current_board(lsb_release_content=output)


    def set_dut_host_info(self, dut_host_info):
        """
        @param dut_host_info: A HostInfo object.
        """
        logging.info('setting dut_host_info field to (%s)', dut_host_info)
        self._dut_host_info = dut_host_info


    def get_dut_host_info(self):
        """
        @return A HostInfo object.
        """
        return self._dut_host_info


    def set_dut_hostname(self, dut_hostname):
        """
        @param dut_hostname: hostname of the DUT that connected to this servo.
        """
        logging.info('setting dut_hostname as (%s)', dut_hostname)
        self._dut_hostname = dut_hostname


    def get_dut_hostname(self):
        """
        @returns hostname of the DUT that connected to this servo.
        """
        return self._dut_hostname

    def is_containerized_servod(self):
        """Checks whether the servo host is a containerized servod.

        @returns: True if using containerized servod, otherwise False.

        """
        return self._is_containerized_servod

    def reboot(self, *args, **dargs):
        """Reboot using special servo host reboot command."""
        super(BaseServoHost, self).reboot(reboot_cmd=self.REBOOT_CMD,
                                          *args, **dargs)

    def run(self, command, timeout=3600, ignore_status=False,
        stdout_tee=utils.TEE_TO_LOGS, stderr_tee=utils.TEE_TO_LOGS,
        connect_timeout=30, ssh_failure_retry_ok=False,
        options='', stdin=None, verbose=True, args=()):
        """Run a command on the servo host.

        Extends method `run` in SSHHost. If the servo host is a remote device,
        it will call `run` in SSHost without changing anything.
        If the servo host is 'localhost', it will call utils.system_output.

        @param command: The command line string.
        @param timeout: Time limit in seconds before attempting to
                        kill the running process. The run() function
                        will take a few seconds longer than 'timeout'
                        to complete if it has to kill the process.
        @param ignore_status: Do not raise an exception, no matter
                              what the exit code of the command is.
        @param stdout_tee/stderr_tee: Where to tee the stdout/stderr.
        @param connect_timeout: SSH connection timeout (in seconds)
                                Ignored if host is 'localhost'.
        @param options: String with additional ssh command options
                        Ignored if host is 'localhost'.
        @param ssh_failure_retry_ok: when True and ssh connection failure is
                                     suspected, OK to retry command (but not
                                     compulsory, and likely not needed here)
        @param stdin: Stdin to pass (a string) to the executed command.
        @param verbose: Log the commands.
        @param args: Sequence of strings to pass as arguments to command by
                     quoting them in " and escaping their contents if necessary.

        @returns: A utils.CmdResult object.

        @raises AutoservRunError if the command failed.
        @raises AutoservSSHTimeout SSH connection has timed out. Only applies
                when servo host is not 'localhost'.

        """

        logging.info("Trying to run the command %s", command)
        client = docker.from_env(timeout=300)
        container = client.containers.get(self.hostname)
        try:
            (exit_code, output) = container.exec_run("bash -c '%s'" % command)
        except docker.errors.APIError:
            logging.exception("Failed to run command %s", command)
            for line in container.logs().split(b'\n'):
                logging.error(line.decode('utf-8'))
            return utils.CmdResult(command=command, stdout="", exit_status=-1)
        return utils.CmdResult(
            command=command, stdout=output, exit_status=exit_code
        )

    def _mount_drive(self, src_path, dst_path):
        """Mount an external drive on servohost.

        @param: src_path  the drive path to mount(e.g. /dev/sda3).
        @param: dst_path  the destination directory on servohost to mount
                          the drive.

        @returns: True if mount success otherwise False.
        """
        # Make sure the dst dir exists.
        self.run('mkdir -p %s' % dst_path)

        result = self.run('mount -o ro %s %s' % (src_path, dst_path),
                          ignore_status=True)
        return result.exit_status == 0

    def _unmount_drive(self, mount_path):
        """Unmount a drive from servohost.

        @param: mount_path  the path on servohost to unmount.

        @returns: True if unmount success otherwise False.
        """
        result = self.run('umount %s' % mount_path, ignore_status=True)
        return result.exit_status == 0

    def is_up(self, timeout=60, connect_timeout=None, base_cmd="true"):
        """
        Check if the remote host is up by ssh-ing and running a base command.

        @param timeout: command execution timeout in seconds.
        @param connect_timeout: ssh connection timeout in seconds.
        @param base_cmd: a base command to run with ssh. The default is 'true'.
        @returns True if the remote host is up before the timeout expires,
                 False otherwise.
        """
        client = docker.from_env(timeout=300)
        try:
            (exit_code, output) = client.containers.get(self.hostname).exec_run(
                "servodtool instance wait-for-active -p 9999")
            logging.info("Is Up output %s", output)
            if exit_code != 0:
                return False
        except docker.errors.NotFound:
            return False
        return True
