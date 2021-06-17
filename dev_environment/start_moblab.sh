#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

( stop_moblab.sh )

docker stop compose || true
docker system prune -f

REGIPADDR=$(hostname -i | awk -F ' ' '{print $1}')
docker volume create --name=leases

REGISTRY_URI="${REGIPADDR}:5000"

docker run \
    --rm \
    -d \
    --name compose \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e LABEL=${USER} \
    -e REGISTRY_URI=${REGISTRY_URI} \
    -e SSH_PORT=2222 \
    ${REGISTRY_URI}/moblab-compose:${USER} up
sleep 10
docker exec -it compose docker-compose logs -f
