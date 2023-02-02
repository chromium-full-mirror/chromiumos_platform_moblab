#!/bin/bash
# Copyright 2023 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x
set -e

BUILD_CONTAINER_REGISTRY=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
BUILD_CONTAINER_REGISTRY_DEV=us-docker.pkg.dev/chromeos-partner-moblab-dev/base-containers
container=partner-testing-rsa

# clone the repo where the sshkeys exist
git clone https://chrome-internal.googlesource.com/chromeos/sshkeys

cd sshkeys

# add the dockerfile for building the docker image 
cat > Dockerfile <<EOT
FROM alpine:latest

COPY /partner_testing_rsa .
EOT

# build the docker image
docker build -t "${container}" .

docker tag "${container}" "${BUILD_CONTAINER_REGISTRY}/${container}"
docker push "${BUILD_CONTAINER_REGISTRY}/${container}"
docker tag "${container}" "${BUILD_CONTAINER_REGISTRY_DEV}/${container}"
docker push "${BUILD_CONTAINER_REGISTRY_DEV}/${container}"

cd ..
# clean the mess
rm -rf sshkeys

