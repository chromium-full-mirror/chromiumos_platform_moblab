#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

docker exec compose /compose_startup.sh down
docker stop registry
docker system prune -f
docker volume prune -f
docker image prune -f
docker container prune -f
docker run -d -p 5000:5000 --restart=always --name registry \
    gcr.io/chromeos-partner-moblab/registry:2