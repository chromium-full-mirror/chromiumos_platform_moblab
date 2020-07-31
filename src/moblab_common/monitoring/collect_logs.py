# -*- coding: utf-8 -*-
# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple log collection script for Mob* Monitor"""

import docker
import glob
import json
import os
import re
import shutil
import tempfile

from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common import host_connector
from moblab_common.utils import cli


TMPDIR = '/tmp'
TMPDIR_PREFIX = 'moblab_logs_'
LOG_DIRS = {
    'apache_errors': '/var/log/apache',
    'bootup_logs': '/var/log/bootup',
    'moblab_logs': '/var/log/moblab',
    'lsb_release': '/etc/lsb-release',
    'moblab_id': '/home/moblab/.moblab_id',
}

DOCKER_DIR = 'docker'
INSPECT_PREFIX = 'inspect_'
DOCKER_PS_DETAILED = 'docker_ps_detailed'
DOCKER_PS_SUCCINCT = 'docker_ps_succinct'
DOCKER_SUCCINCT_KEYS = ["Command", "Created", "Id", "Image", "ImageID", "Names", "State", "Status"]


def remove_old_tarballs():
  """
  Removes all files in the tmp dir where all log tarballs are created. This is a
  backup, calls to collect_logs should clean up after themselves.
  """
  paths = glob.iglob(os.path.join(TMPDIR, '%s*.tgz' % TMPDIR_PREFIX))
  for path in paths:
    os.remove(path)

def _write_to_file(filename, content):
  """
  :param filename: complete path of file to write content to.
  :param content: String content to be written to disk.
  :return: None
  """
  with open(filename, 'w+') as f:
    f.write(content)

def _filtered_docker_container_info(docker_containers_info):
  """
  :param docker_containers_info: A list of dicts, each dict container a container's
  info.
  :return: A list of dicts, like the input, only with each dict filtered for target
  keys.
  """
  succinct_containers_info = []
  for container in docker_containers_info:
    succinct_containers_info.append({ key: container.get(key, None) for key in DOCKER_SUCCINCT_KEYS})
  return succinct_containers_info


def _get_docker_container_details(write_dir):
  """
  :param filename: complete path of file to write content to.
  :param content: String content to be written to disk.
  :return: None
  """
  docker_api_client = docker.APIClient()
  docker_client = docker.from_env()

  cli.safe_mkdir(os.path.join(write_dir, DOCKER_DIR))

  detailed_container_info = docker_api_client.containers()
  _write_to_file(
      os.path.join(write_dir, DOCKER_DIR, DOCKER_PS_DETAILED + '.log'),
      json.dumps(detailed_container_info, indent=4, sort_keys=True)
  )

  succinct_container_info = _filtered_docker_container_info(detailed_container_info)
  _write_to_file(
      os.path.join(write_dir, DOCKER_DIR, DOCKER_PS_SUCCINCT + '.log'),
      json.dumps(succinct_container_info, indent=4, sort_keys=True)
  )

  for container in docker_client.containers.list():
    _write_to_file(
        os.path.join(write_dir, DOCKER_DIR, INSPECT_PREFIX + container.name + '.log'),
        json.dumps(docker_api_client.inspect_container(container.id), indent=4, sort_keys=True)
    )

def collect_logs():
  """
  Collects all available Moblab logs and docker configuration information.
  :return: Path to tarball of collected logs and info.
  """
  remove_old_tarballs()
  cli.safe_mkdir(TMPDIR)

  with tempfile.TemporaryDirectory(prefix=TMPDIR_PREFIX, dir=TMPDIR) as tempdir:
    os.chmod(tempdir, 0o777)
    try:
      for name, path in LOG_DIRS.items():
        if not os.path.exists(path):
          continue
        if os.path.isdir(path):
          shutil.copytree(path, os.path.join(tempdir, name), ignore_dangling_symlinks=True)
        else:
          shutil.copyfile(path, os.path.join(tempdir, name), follow_symlinks=False)

      status_file = os.path.join(tempdir, 'mobmonitor_getstatus')
      status = cli.run_command([
              'curl', 'http://localhost:9991/GetStatus', '-o', status_file])

      serialfile = os.path.join(tempdir, 'serialno')
      _write_to_file(serialfile, host_connector.HostServicesConnector().get_host_identifier())

      afe = afe_connector.AFEConnector()
      conf = config_connector.MoblabConfigConnector(afe)
      conf.load_config()
      configfile = os.path.join(tempdir, 'config')
      _write_to_file(configfile, str(conf.config))

      _get_docker_container_details(tempdir)
    finally:
      tarball = '%s.tgz' % tempdir
      cli.create_tarball(tarball, tempdir[len(TMPDIR + '/'):], TMPDIR)

  return tarball
