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
   DB_UP=$(mysql -h db -u chromeosqa-admin -p${passwd} \
    -e "SELECT 1")
done

ACL_GROUP_AVAILABLE=$(mysql -h db  -uroot -p${passwd} -Dchromeos_autotest_db \
    -e "select count(*) from afe_acl_groups")
while [ -z "${ACL_GROUP_AVAILABLE}" ]; do
   sleep 1
   ACL_GROUP_AVAILABLE=$(mysql -h db  -uroot -p${passwd} -Dchromeos_autotest_db \
    -e "select count(*) from afe_acl_groups")
done

export PYTHONPATH=/usr/local/autotest/venv:/usr/local/autotest

/usr/local/autotest/scheduler/monitor_db.py --production /usr/local/autotest/results