# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM docker/compose:alpine-1.25.4

COPY docker-compose.yaml .

# TODO figure out how to run the container as moblab
RUN addgroup --gid 246 moblab && adduser --ingroup moblab \
    --uid 246 --disabled-password --gecos "" moblab

# Test the config for syntax errors
RUN docker-compose config