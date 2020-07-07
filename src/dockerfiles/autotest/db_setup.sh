#!/bin/bash
set -x
set -e

passwd=moblab_db_passwd
PASSWD_STRING="-p${passwd}"

while ! mysqladmin status -h db -uroot -p${passwd} --silent; do
    sleep 1
done

# Create autotest database
missingdb=
DATABASE_LOOKUP_SQL="SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA \
    WHERE SCHEMA_NAME = 'chromeos_autotest_db'"
EXISTING_DATABASE=$(mysql -h db -u root "${PASSWD_STRING}" \
    -e "${DATABASE_LOOKUP_SQL}")
SQL_CREATE_COMMAND="""
    CREATE DATABASE chromeos_autotest_db;

"""
SQL_GRANT_COMMAND="""
    GRANT ALL privileges ON chromeos_autotest_db.* TO
        'chromeosqa-admin' IDENTIFIED BY '${passwd}';
    FLUSH PRIVILEGES;
"""

if [ -z "${EXISTING_DATABASE}" ]; then
  mysql -h db -u root "${PASSWD_STRING}" -e "${SQL_CREATE_COMMAND}"
fi
mysql -h db -u root "${PASSWD_STRING}" -e "${SQL_GRANT_COMMAND}"


/usr/local/autotest/database/migrate.py sync -f
/usr/local/autotest/frontend/manage.py syncdb --noinput