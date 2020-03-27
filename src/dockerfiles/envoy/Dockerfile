# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM envoyproxy/envoy:latest

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 --disabled-password --gecos "" moblab

COPY --chown=moblab envoy.yaml /etc/envoy/envoy.yaml

USER moblab

CMD /usr/local/bin/envoy -c /etc/envoy/envoy.yaml
