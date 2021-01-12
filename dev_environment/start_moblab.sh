#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

REGIPADDR=$(hostname -i | awk -F ' ' '{print $1}')
docker volume create --name=leases
docker run \
    --rm \
    --name compose \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e LABEL=${USER} \
    -e REGISTRY_URI=${REGIPADDR}:5000 \
    -e SSH_PORT=2222 \
    $(hostname -i | awk -F ' ' '{print $1}'):5000/moblab-compose:${USER} up > /var/log/bootup/moblab-compose-up.log
