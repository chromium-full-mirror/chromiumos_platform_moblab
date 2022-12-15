#!/bin/bash
# Copyright 2022 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

docker exec compose /compose_startup.sh down
docker stop registry
docker system prune -f
docker volume prune -f
docker image prune -f
docker container prune -f