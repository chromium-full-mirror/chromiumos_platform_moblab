# -*- coding: utf-8 -*-
# Copyright 2015 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple log collection script for Mob* Monitor"""

import glob
import os
import tempfile
import shutil

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

def remove_old_tarballs():
  paths = glob.iglob(os.path.join(TMPDIR, '%s*.tgz' % TMPDIR_PREFIX))
  for path in paths:
    os.remove(path)


def collect_logs():
  remove_old_tarballs()
  cli.safe_mkdir(TMPDIR)
  tempdir = tempfile.mkdtemp(prefix=TMPDIR_PREFIX, dir=TMPDIR)
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
    with open(serialfile, 'w+') as f:
      f.write(host_connector.HostServicesConnector().get_host_identifier())

    afe = afe_connector.AFEConnector()
    conf = config_connector.MoblabConfigConnector(afe)
    conf.load_config()
    configfile = os.path.join(tempdir, 'config')
    with open(configfile, 'w+') as f:
      f.write(str(conf.config))

  finally:
    tarball = '%s.tgz' % tempdir
    cli.create_tarball(tarball, tempdir)
    cli.rm_dir(tempdir, ignore_missing=True)
  return tarball
