# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Command line util library"""

import subprocess
import os
import shutil
import logging
import errno
import collections
import re

LOGGER = logging.getLogger(__name__)

class RunCommandError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd):
        super(RunCommandError, self).__init__(returncode, cmd)

def run_command(cmd, error_code_ok=False, log=False, shell=False):
    """Run a command.

    Args:
        cmd: string array of the command, and the command line arguments to
            pass into the command, ex:
                ['echo', 'hello']
        error_code_ok: do not throw RunCommandError on non-zero exit code
        log: log the command and the output

    Return:
        string containing the stdout of the output, None if no output
    """
    try:
        output = subprocess.check_output(cmd, shell=shell)
        if log:
            LOGGER.info(' '.join(cmd))
            LOGGER.info(output)
        return output
    except subprocess.CalledProcessError as e:
        if log:
            LOGGER.info(' '.join(cmd))
            LOGGER.info(str(e))
        if not error_code_ok:
            raise RunCommandError(e.returncode, e.cmd)

def sudo_run_command(cmd, user='root', error_code_ok=False, shell=False):
    """Run a command via sudo. All calls are logged.

    Args:
        cmd: string array of the command and args, see run_command for details
        user: what user to run the command as, default root
        error_code_ok: do not throw RunCommandError on non-zero exit code

    Return:
        string containing stdout of the output, None if no output
    """
    if user == 'root':
        sudo_cmd = ['sudo'] + cmd
    else:
        sudo_cmd = ['sudo', '-u', user] + cmd
    return run_command(sudo_cmd, log=True, error_code_ok=error_code_ok,
            shell=shell)

def create_tarball(tarball_name, directory):
    """Creates a gzipped tar archive

    Args:
        tarball_name: string name for the tarball
        directory: directory to archive the contents of
    """
    run_command(['tar', '-czf', tarball_name, directory])

def safe_mkdir(path):
    """Create a directory and any parent directories if they don't exist.

    Args:
        path: string path of the new directory
    """
    run_command(['mkdir', '-p', path])

def rm_dir(path, ignore_missing=False, sudo=False):
  """Recursively remove a directory.

  Args:
    path: Path of directory to remove.
    ignore_missing: Do not error when path does not exist.
    sudo: Remove directories as root.
  """
  if sudo:
    try:
      sudo_run_command(
          ['rm', '-r%s' % ('f' if ignore_missing else '',), '--', path])
    except RunCommandError as e:
      if not ignore_missing or os.path.exists(path):
        # If we're not ignoring the rm ENOENT equivalent, throw it;
        # if the pathway still exists, something failed, thus throw it.
        raise
  else:
    try:
      shutil.rmtree(path)
    except EnvironmentError as e:
      if not ignore_missing or e.errno != errno.ENOENT:
        raise

def resolve_symlink(file_name, root='/'):
    """Resolve a symlink |file_name| relative to |root|.

    For example:

        ROOT-A/absolute_symlink --> /an/abs/path
        ROOT-A/relative_symlink --> a/relative/path

        absolute_symlink will be resolved to ROOT-A/an/abs/path
        relative_symlink will be resolved to ROOT-A/a/relative/path

    Args:
        file_name: A path to the file.
        root: A path to the root directory.

    Returns:
        file_name if file_name is not a symlink. Otherwise, the ultimate path
        that file_name points to, with links resolved relative to |root|.
    """
    count = 0
    while os.path.islink(file_name):
        count += 1
        if count > 128:
            raise ValueError('Too many link levels for %s.' % file_name)
        link = os.readlink(file_name)
        if link.startswith('/'):
            file_name = os.path.join(root, link[1:])
        else:
            file_name = os.path.join(os.path.dirname(file_name), link)
    return file_name

def list_block_devices():
    """Lists all block devices.

    Returns:
        A list of BlockDevice items with attributes 'NAME', 'RM', 'TYPE',
        'SIZE' (RM stands for removable).
    """
    keys = ['NAME', 'RM', 'TYPE', 'SIZE']
    BlockDevice = collections.namedtuple('BlockDevice', keys)

    cmd = ['lsblk', '--pairs', '--bytes']
    cmd += ['--output', ','.join(keys)]

    output = run_command(cmd).strip()
    devices = []
    for line in output.splitlines():
        d = {}
        for k, v in re.findall(r'(\S+?)=\"(\w*?)\"', line):
            d[k] = v

        devices.append(BlockDevice(**d))

    return devices


def list_connected_dut_ips():
    """List duts by ip currently connected to test subnet

    Returns:
        A list of connected ips on the test subnet
    """

    # regex to search an ip n reachable or cached line such as
    # 192.168.231.100 dev lxcbr0 lladdr 60:38:e0:e3:10:f5 STALE
    # grabs ip, state
    # note this will not match an 'INCOMPLETE' line that indicates
    # no network connection
    regex = re.compile('^(192\.168\.231\.1\d\d)\sdev\s\S+\slladdr\s\S+\s(\S+)')

    duts = []
    ip_n_output = run_command(['ip', 'n']).strip()
    for line in ip_n_output.splitlines():
        match = regex.search(line)
        if match is not None:
            ip = match.group(1)
            state = match.group(2)
            if state == 'REACHABLE':
                duts.append(ip)
            else:
                # a stale record, ping the ip to be sure it is reachable
                cmd = ['ping', '-c', '1', '-W', '1', ip]
                ping_output = run_command(cmd, error_code_ok=True)
                if (ping_output is not None and
                        '64 bytes from %s' % ip in ping_output):
                    duts.append(ip)

    return duts
