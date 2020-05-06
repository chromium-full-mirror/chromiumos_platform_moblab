#!/bin/bash
set -x

passwd=moblab_db_passwd
DB_UP=$(mysql -h db -u root -p${passwd} \
    -e "SELECT 1")
while [ -z "${DB_UP}" ]; do
   sleep 1
   DB_UP=$(mysql -h db -u root -p${passwd} \
    -e "SELECT 1")
done

clobberdb=
DATABASE_LOOKUP_SQL="SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA \
    WHERE SCHEMA_NAME = 'chromeos_autotest_db'"
EXISTING_DATABASE=$(mysql -h db -u root -p${passwd} \
    -e "${DATABASE_LOOKUP_SQL}")
while [ -z "${EXISTING_DATABASE}" ]; do
  sleep 1
  EXISTING_DATABASE=$(mysql -h db -u root -p${passwd} \
    -e "${DATABASE_LOOKUP_SQL}")
done

/usr/local/autotest/database/migrate.py sync -f
/usr/local/autotest/frontend/manage.py syncdb --noinput