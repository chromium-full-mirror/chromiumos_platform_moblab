#!/bin/bash
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x
set -e

BUILD_CONTAINER_REGISTRY=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
CONTAINERS=(alpine/git
            alpine:edge
            blacklabelops/logrotate:latest
            bufbuild/buf
            containrrr/watchtower:latest
            debian:buster
            debian:buster-slim
            docker:latest
            envoyproxy/envoy:v1.15.2
            hadolint/hadolint:latest-debian
            linuxserver/openssh-server:latest
            mariadb:10.5
            nginx:alpine
            node:12-buster
            node:15
            python:2-buster
            python:2.7-slim-buster
            python:3.8-buster
            python:3.8-slim-buster)

for container in $CONTAINERS
do
    docker pull "${container}"
    docker tag "${container}" "${BUILD_CONTAINER_REGISTRY}/${container}"
    docker push "${BUILD_CONTAINER_REGISTRY}/${container}"
done