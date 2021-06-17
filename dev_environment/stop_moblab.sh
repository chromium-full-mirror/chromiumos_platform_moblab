#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x
 
docker exec compose docker-compose -f ./docker-compose.watchtower.yaml rm -s -f
docker exec compose docker-compose rm -s -f
docker stop compose
docker system prune -f
