# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM alpine:edge

# fetch dnsmasq
RUN apk update \
    && apk --no-cache add dnsmasq libcap
#configure dnsmasq
RUN mkdir -p /etc/default/
RUN echo -e "ENABLED=1\nIGNORE_RESOLVCONF=yes" > /etc/default/dnsmasq
COPY dnsmasq.conf /etc/dnsmasq.conf


ENTRYPOINT ["/usr/sbin/dnsmasq","--no-daemon"]
