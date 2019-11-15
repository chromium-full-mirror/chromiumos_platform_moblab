#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Tool for generating a moblab id"""

from __future__ import print_function

import grp
import os
import pwd

from moblab_common import moblab_info


if __name__ == '__main__':
    moblab_info.get_or_create_id()
    uid = pwd.getpwnam(moblab_info.MOBLAB_USER).pw_uid
    gid = grp.getgrnam(moblab_info.MOBLAB_GROUP).gr_gid
    os.chown(moblab_info.MOBLAB_ID_FILENAME, uid, gid)
