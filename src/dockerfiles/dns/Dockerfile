# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers

FROM ${BASE_REGISTRY_URI}/alpine:edge

# fetch dnsmasq
RUN apk update \
    && apk --no-cache add dnsmasq libcap
#configure dnsmasq
RUN mkdir -p /etc/default/
RUN echo -e "ENABLED=1\nIGNORE_RESOLVCONF=yes" > /etc/default/dnsmasq
COPY dnsmasq.conf /etc/dnsmasq.conf

# We run dnsmasq as the moblab user by passing in --user and --group
# params to the command in startup.sh.
COPY startup.sh /
RUN chmod u+x /startup.sh
RUN addgroup --gid 246 moblab && adduser --ingroup moblab \
    --uid 246 --disabled-password --gecos "" moblab

RUN mkdir -p /var/log
RUN chown -R moblab:moblab /var/log

CMD ["/startup.sh"]
