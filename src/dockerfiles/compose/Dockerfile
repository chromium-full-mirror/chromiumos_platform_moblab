# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM docker/compose:alpine-1.25.4

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release
ARG WATCHTOWER_CMD="--interval 3600 --monitor-only"

ENV LABEL="${LABEL}"
ENV REGISTRY_URI="${REGISTRY_URI}"
ENV WATCHTOWER_CMD="${WATCHTOWER_CMD}"

COPY docker-compose.yaml .

# Test the config for syntax errors
RUN docker-compose config