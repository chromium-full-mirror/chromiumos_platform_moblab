#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

# This script assumes an $LABEL is set of autopush/beta/release or a custom label
# for development

echo "Enviroment variable LABEL is ${LABEL}"

# The checked in code assumes autopush build, convert this to a beta/release
# build container on startup.  Autopush/custom builds can be overridden by the
# user and those .env files should not be changed.
if [ "${LABEL}" == "release" ] || [ "${LABEL}" == "beta" ]; then
  sed -i.bak s/autopush/${LABEL}/g .env
fi

echo "Command is ${1}"

if [ "${1}" == "down" ]
then
    docker-compose stop -t 30 db
    docker-compose down -t 30
    docker-compose rm -s -f
else
    # This is in case the device was not shutdown cleanly there might be
    # restarted containers (restarted by dockerd)
    docker-compose down -t 300

    docker-compose pull remote_access
    docker-compose up -d remote_access

    docker-compose pull db db-init autotest autotest-dbsetup
    docker-compose up -d db db-init autotest autotest-dbsetup

    docker-compose pull devserver autotest-monitordb autotest-hostscheduler
    docker-compose up -d devserver autotest-monitordb autotest-hostscheduler

    docker-compose pull
    docker-compose up -d
    docker system prune -f
    docker-compose logs -f
fi
