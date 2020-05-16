# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM docker/compose:alpine-1.25.4

COPY docker-compose.yaml .

ENV LABEL=${LABEL}
ENV REGISTRY_URI=${REGISTRY_URI}

# Test the config for syntax errors
RUN docker-compose config