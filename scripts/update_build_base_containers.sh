#!/bin/bash
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x
set -e

BUILD_CONTAINER_REGISTRY=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
BUILD_CONTAINER_REGISTRY_DEV=us-docker.pkg.dev/chromeos-partner-moblab-dev/base-containers
CONTAINERS=(
    alpine/git
    alpine:edge
    blacklabelops/logrotate:latest
    bufbuild/buf
    containrrr/watchtower:latest
    debian:buster
    debian:buster-slim
    docker/dockerfile-copy:v0.1.9
    docker:latest
    docker/compose:alpine-1.27.4
    envoyproxy/envoy:v1.15.2
    hadolint/hadolint:latest-debian
    linuxserver/openssh-server:latest
    mariadb:10.5
    nginx:alpine
    node:18-buster
    node:18
    python:3.7-buster
    python:3.7-slim-buster
    python:3.8-buster
    python:3.8-slim-buster
    v2tec/watchtower:latest
    )

for container in ${CONTAINERS[@]}
do
    docker pull "${container}"
    docker tag "${container}" "${BUILD_CONTAINER_REGISTRY}/${container}"
    docker push "${BUILD_CONTAINER_REGISTRY}/${container}"
    docker tag "${container}" "${BUILD_CONTAINER_REGISTRY_DEV}/${container}"
    docker push "${BUILD_CONTAINER_REGISTRY_DEV}/${container}"
done
