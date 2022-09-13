# Copyright 2022 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x

# need to set the restart status to NO, to ensure containers
# don't restart automatically. Unfortunately there is no good
# way to find the moblab containers, so setting the status
# of all the active docker containers
docker update --restart=no $(docker ps -q)

docker exec -i compose /compose_startup.sh down

docker stop compose
docker system prune -f
