#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Tool for generating a moblab id"""
#TODO(haddowk)  refactor the code and break the dependency on autotest.

from __future__ import print_function

import common
import grp
import os
import pwd

from autotest_lib.client.common_lib import utils

MOBLAB_USER = "moblab"
MOBLAB_GROUP = "moblab"
MOBLAB_ID_FILENAME = "/home/moblab/.moblab_id"

if __name__ == '__main__':
    utils.get_moblab_id()
    uid = pwd.getpwnam(MOBLAB_USER).pw_uid
    gid = grp.getgrnam(MOBLAB_GROUP).gr_gid
    os.chown(MOBLAB_ID_FILENAME, uid, gid)
