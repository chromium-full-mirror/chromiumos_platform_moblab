# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers

FROM ${BASE_REGISTRY_URI}/docker/compose:alpine-1.27.4

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release
ARG WATCHTOWER_CMD="--interval 3600 --monitor-only"
ARG SSH_PORT

ENV LABEL="${LABEL}"
ENV REGISTRY_URI="${REGISTRY_URI}"
ENV WATCHTOWER_CMD="${WATCHTOWER_CMD}"
ENV SSH_PORT="${SSH_PORT}"

WORKDIR /
COPY docker-compose.yaml .
COPY docker-compose.override.yaml* .
COPY .env main.env
COPY override.env* .
COPY compose_startup.sh .
RUN chmod u+x compose_startup.sh

ENTRYPOINT ["/compose_startup.sh"]

# Test the config for syntax errors
RUN docker-compose config
