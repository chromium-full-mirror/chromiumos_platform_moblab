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

# Create autotest database
clobberdb=
DATABASE_LOOKUP_SQL="SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA \
    WHERE SCHEMA_NAME = 'chromeos_autotest_db'"
EXISTING_DATABASE=$(mysql -h db -u root "${PASSWD_STRING}" \
    -e "${DATABASE_LOOKUP_SQL}")
if [ -z "${EXISTING_DATABASE}" ]; then
  clobberdb=true
fi

SQL_COMMAND="drop database if exists chromeos_autotest_db; \
    create database chromeos_autotest_db; \
    grant all privileges on chromeos_autotest_db.* TO \
    'chromeosqa-admin' identified by '${passwd}'; \
    FLUSH PRIVILEGES;"

if [ "${clobberdb}" = true ]; then
  mysql -h db -u root "${PASSWD_STRING}" -e "${SQL_COMMAND}"
fi

