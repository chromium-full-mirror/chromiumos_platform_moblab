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

# tuple for carrying holding arguments for a cp operation.
# src: path to file to copy on local machine
# name: filename of the copy
CopyFile = collections.namedtuple('CopyFile', ['src', 'name'])

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
    return run_command(cmd, log=True, error_code_ok=error_code_ok,
            shell=shell)

def create_tarball(tarball_name, directory, starting_directory=None):
    """Creates a gzipped tar archive

    Args:
        tarball_name: string name for the tarball
        directory: directory to archive the contents of
        starting_directory: context directory to find directory within (
          useful for hiding undesired parent directory structures )
    """
    args = ['-czf', tarball_name, directory]
    if starting_directory:
      args = ['-C', starting_directory] + args
    args = ['tar'] + args
    run_command(args)

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
        if link.startswith(b'/'):
            file_name = os.path.join(root, link[1:])
        else:
            file_name = os.path.join(os.path.dirname(file_name), link)
    return file_name

# TODO(chromium:1114972): Consolidate perfdiag usage in the Moblab code base.
def run_gcloud_bucket_diagnosis(output_file, bucket_name):
    """Run performance diagnosis on the given google storage bucket.

    Args:
        output_file: A path to the output file.
        bucket_name: The google storage bucket name.

    Raises:
        RunCommandError if the command fails to run.
    """
    try:
      run_command(
          ['gsutil perfdiag -o %s -s 40M gs://%s' % (output_file, bucket_name)],
          log=True, shell=True)
    except RunCommandError as err:
        LOGGER.exception('Failed to run performance diagnosis on given google storage bucket: %s'
                         % err)
        raise
