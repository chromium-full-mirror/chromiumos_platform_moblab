#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

docker run --rm --net host -e SOURCE_ROOT=$(pwd)/moblab \
    --env DISPLAY=unix$DISPLAY --privileged \
    --volume /tmp/.X11-unix:/tmp/.X11-unix  --shm-size=5g --user $USER \
    --ulimit nofile=200000:200000 -e USER=$USER -v $HOME:/home/$USER \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(pwd):/moblab_source -it -t mymoblabdev:latest
