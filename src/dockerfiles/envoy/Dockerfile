# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Crashing on Moblab
#FROM envoyproxy/envoy:v1.16.0

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers

FROM ${BASE_REGISTRY_URI}/envoyproxy/envoy:v1.15.2

ARG UID=246

RUN addgroup --gid $UID moblab && adduser --ingroup moblab --uid $UID --disabled-password --gecos "" moblab

COPY --chown=moblab envoy.yaml /etc/envoy/envoy.yaml

USER moblab

CMD /usr/local/bin/envoy -c /etc/envoy/envoy.yaml
