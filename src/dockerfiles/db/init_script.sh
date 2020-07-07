#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x

#TODO - remove hard coded passwords, this one is already checked for
# existing moblab so we are not leaking anything new.

passwd=moblab_db_passwd
PASSWD_STRING="-p${passwd}"

while ! mysqladmin status -h db -uroot -p${passwd} --silent; do
    sleep 1
done

# In the case we have updated to a new version of the db - upgrade
mysqlcheck -h db --no-defaults --fix-db-names --fix-table-names -uroot \
     "${PASSWD_STRING}" --all-databases -v
mysqlcheck -h db --no-defaults --check-upgrade --auto-repair -uroot \
     "${PASSWD_STRING}" --all-databases -v

