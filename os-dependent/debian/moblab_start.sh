#!/bin/bash
# Copyright 2022 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

source moblab_setup_configuration.conf

mkdir -p /var/log/bootup/
set -x
set -e

track=${CHANNEL}

case $track in

  beta-channel)
    LABEL=beta
  ;;

  testimage-channel | dev-channel | developer-build )
    LABEL=${DEV_LABEL}
    REPO_ADDR=${DEV_REPO_ADDR}
  ;;
esac

case $track in
  testimage-channel )
    SSH_PORT=2222
  ;;
esac

# check docker info
reps=0
while [ ${reps} -lt 100 ] && ! docker info ; do
  : $((reps += 1))
  sleep 1
done

docker stop compose || true
docker rm compose || true

# pull latest docker-compose container for moblab
reps=0
while [ ${reps} -lt 100 ] && \
      ! docker pull \
        "${REPO_ADDR}/moblab-compose:${LABEL}" ; do
  : $((reps += 1))
  sleep 1
done

docker run --restart unless-stopped --name compose \
  --label=com.centurylinklabs.watchtower.lifecycle.pre-update="docker-compose down" \
  --label=com.centurylinklabs.watchtower.stop-signal=KILL \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e LABEL=${LABEL} \
  -e SSH_PORT=${SSH_PORT} \
  -d \
  "${REPO_ADDR}/moblab-compose:${LABEL}" up

echo 'execute: "docker logs -f compose" to look at logs'
