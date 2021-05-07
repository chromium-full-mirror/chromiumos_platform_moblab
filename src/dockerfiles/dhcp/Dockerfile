# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers

FROM ${BASE_REGISTRY_URI}/alpine:edge

# fetch dnsmasq and webproc binary
RUN apk update \
    && apk --no-cache add dnsmasq libcap

#configure dnsmasq
RUN mkdir -p /etc/default/
RUN echo -e "ENABLED=1\nIGNORE_RESOLVCONF=yes" > /etc/default/dnsmasq
COPY dnsmasq.conf /etc/dnsmasq.conf
COPY dnsmasq-dev.conf /etc/dnsmasq-dev.conf

#run!
ENTRYPOINT ["/usr/sbin/dnsmasq","--no-daemon"]
