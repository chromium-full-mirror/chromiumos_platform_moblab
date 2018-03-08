#!/usr/bin/python
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import subprocess
import re
import sys

usage = ('USAGE: %s <release_number>\n  '
         '  <release_number> is RXX, R64, R65 etc') % sys.argv[0]

if len(sys.argv) != 2:
  print usage
  exit(1)

home = os.path.expanduser('~')
trunk = '%s/trunk/src/' % home

repos = [
  'platform/moblab',
  'third_party/autotest/files',
  'overlays',
  'third_party/whining',
  'third_party/portage-stable',
]

try:
  release_number_int = int(sys.argv[1][1:])
except ValueError:
  print usage
  exit(1)

def get_branch(release_number):
  os.chdir('%s/platform/moblab' % trunk)
  cmd = 'git branch -a | grep release-R%d' % release_number
  return subprocess.check_output([cmd], shell=True).strip()

release = get_branch(release_number_int)
previous_release = get_branch(release_number_int -1)
cmd = ("git --no-pager log --cherry --pretty=format:'%h - %s (%ae %cr)'"
       ' {1}...{0} | '
       "grep -E 'moblab|mattmallett|haddowk'").format(release, previous_release)

for repo in repos:
  repo_path = '%s%s' % (trunk, repo)
  try:
    os.chdir(repo_path)
    commits = subprocess.check_output([cmd], shell=True)
    print repo, '\n'
    print commits
    print '\n'
  except Exception as e:
    print repo, '\n'
    print 'no changes', '\n'

