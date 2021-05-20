#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

# This script assumes an $LABEL is set of autopush/beta/release or a custom label
# for development

echo "Enviroment variable LABEL is ${LABEL}"
echo "Enviroment variable REGISTRY_URI is ${REGISTRY_URI}"


echo "Merging main.env and override.env into .env"
egrep -oh '^[^#]+' main.env override.env | egrep . | awk -F= '{a[$1]=$2}END{for(i in a) print i "=" a[i]}' > .env

# The only process that stores state in the system is the database.
# in prodution give the database type to stop cleanly to ensure tables
# are not corrupted, everything else can be taken down fast.
TIMEOUT=1

echo "Command is ${1}"

# Stop any old style docker containers that are named default_
/usr/local/bin/docker stop $(/usr/local/bin/docker ps --filter name="default_" --format "{{.ID}}")

if [ "${1}" == "down" ]
then
    docker-compose stop -t ${TIMEOUT} db
    docker-compose down -t 1
    docker-compose rm -s -f

    docker-compose -f ./docker-compose.watchtower.yaml down -t 1

else
    # This is in case the device was not shutdown cleanly there might be
    # restarted containers (restarted by dockerd)
    docker-compose down -t 1
    docker-compose -f ./docker-compose.watchtower.yaml down -t 1

    #!! docker-compose creates all the volumes on first docker-compose up
    #!! remote_access is initializing moblab_home volume with ssh key
    #!! so it has to be on first docker-compose up
    docker-compose pull moblab-ui remote_access
    docker-compose up -d moblab-ui remote_access

    docker-compose pull mobmonitor
    docker-compose up -d mobmonitor

    docker-compose -f ./docker-compose.watchtower.yaml pull
    docker-compose -f ./docker-compose.watchtower.yaml up -d

    docker-compose pull db db-init db-setup dns autotest-afe autotest-dbsetup
    docker-compose up -d db db-init db-setup dns autotest-afe autotest-dbsetup

    docker-compose pull devserver autotest-monitor-db autotest-hostscheduler
    docker-compose up -d devserver autotest-monitor-db autotest-hostscheduler

    docker-compose pull
    docker-compose up -d
    docker system prune -f
    docker-compose logs -f
fi
