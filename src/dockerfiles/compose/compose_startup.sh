#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

# This script assumes an $LABEL is set of autopush/beta/release or a custom label
# for development

echo "Enviroment variable LABEL is ${LABEL}"


echo "Merging main.env and override.env into .env"
egrep -oh '^[^#]+' main.env override.env | egrep . | awk -F= '{a[$1]=$2}END{for(i in a) print i "=" a[i]}' > .env

# The only process that stores state in the system is the database.
# in prodution give the database type to stop cleanly to ensure tables
# are not corrupted, everything else can be taken down fast.
TIMEOUT=1
# The checked in code assumes  autopush build, convert this to a beta/release
# build container on startup.  Autopush/custom builds can be overridden by the
# user and those .env files should not be changed.
if [ "${LABEL}" == "release" ] || [ "${LABEL}" == "beta" ]; then
  sed -i.bak s/autopush/${LABEL}/g .env
  TIMEOUT=30
fi

echo "Command is ${1}"

if [ "${1}" == "down" ]
then
    docker-compose stop -t ${TIMEOUT} db
    docker-compose down -t 1
    docker-compose rm -s -f

elif [ "${1}" == "db" ]
then

    echo "Starting up db!"

    docker-compose down

    docker-compose pull db db-init db-setup
    docker-compose up db db-init db-setup

else
    # This is in case the device was not shutdown cleanly there might be
    # restarted containers (restarted by dockerd)
    docker-compose down -t 1

    docker-compose pull remote_access moblab-ui
    docker-compose up -d remote_access moblab-ui

    docker-compose pull db db-init db-setup dns autotest-afe autotest-dbsetup
    docker-compose up -d db db-init db-setup dns autotest-afe autotest-dbsetup

    docker-compose pull devserver autotest-monitor-db autotest-hostscheduler
    docker-compose up -d devserver autotest-monitor-db autotest-hostscheduler

    docker-compose pull
    docker-compose up -d
    docker system prune -f
    docker-compose logs -f
fi
