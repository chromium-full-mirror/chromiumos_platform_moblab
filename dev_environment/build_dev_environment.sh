#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

curl https://chromium.googlesource.com/chromiumos/platform/moblab/+/refs/heads/master/build_environment/Dockerfile?format=TEXT \
    | base64 -d > Dockerfile

curl https://chromium.googlesource.com/chromiumos/platform/moblab/+/refs/heads/master/build_environment/moblab_build_env.sh?format=TEXT \
    | base64 -d > Dockerfile

docker build -t mymoblabdev --build-arg USER=$USER --build-arg  USERID=$(id -u) .

echo "Installing script that starts build environment."
sudo install moblab_build_env.sh

xhost +
