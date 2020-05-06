#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

passwd=moblab_db_passwd

DB_UP=$(mysql -h db -u root -p${passwd} \
    -e "SELECT 1")
while [ -z "${DB_UP}" ]; do
   sleep 1
   DB_UP=$(mysql -h db -u root -p${passwd} \
    -e "SELECT 1")
done

/usr/local/autotest/scheduler/monitor_db.py --production /usr/local/autotest/results