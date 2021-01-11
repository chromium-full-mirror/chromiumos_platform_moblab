#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

curl https://chromium.googlesource.com/chromiumos/platform/moblab/+/refs/heads/main/dev_environment/Dockerfile?format=TEXT \
    | base64 -d > Dockerfile
curl https://chromium.googlesource.com/chromiumos/platform/moblab/+/refs/heads/main/dev_environment/start_dev_environment.sh?format=TEXT \
    | base64 -d > start_dev_environment.sh
curl https://chromium.googlesource.com/chromiumos/platform/moblab/+/refs/heads/main/dev_environment/start_moblab.sh?format=TEXT \
    | base64 -d > start_moblab.sh
curl https://chromium.googlesource.com/chromiumos/platform/moblab/+/refs/heads/main/dev_environment/stop_moblab.sh?format=TEXT \
    | base64 -d > stop_moblab.sh
curl https://chromium.googlesource.com/chromiumos/platform/moblab/+/refs/heads/main/dev_environment/reset_moblab.sh?format=TEXT \
    | base64 -d > reset_moblab.sh

docker pull gcr.io/chromeos-partner-moblab/moblab-dev-environment:autopush
docker build -t mymoblabdev --build-arg USER=$USER --build-arg  USERID=$(id -u) .

echo "Installing script that starts build environment."
sudo install start_dev_environment.sh /usr/local/bin
sudo install start_moblab.sh /usr/local/bin
sudo install stop_moblab.sh /usr/local/bin
sudo install reset_moblab.sh /usr/local/bin

xhost +
