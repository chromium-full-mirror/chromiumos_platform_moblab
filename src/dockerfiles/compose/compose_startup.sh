#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

# This script assumes an $LABEL is set of autopush/beta/release or a custom label
# for development

echo "Enviroment variable LABEL is ${LABEL}"

echo "Command is ${1}"

if [ "${1}" == "down" ]
then
    docker-compose stop -t 30 db
    docker-compose down -t 30
else
    docker-compose pull remote_access
    docker-compose up -d --no-recreate -e SSH_PORT=${SSH_PORT} remote_access

    docker-compose pull db db-init autotest autotest-dbsetup
    docker-compose up -d --no-recreate db db-init autotest autotest-dbsetup

    docker-compose pull devserver autotest-monitordb autotest-hostscheduler
    docker-compose up -d --no-recreate devserver autotest-monitordb autotest-hostscheduler

    docker-compose pull
    docker-compose up -d --no-recreate
    docker system prune -f
    docker-compose logs -f
fi
