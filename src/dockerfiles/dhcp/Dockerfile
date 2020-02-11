# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM alpine:edge

# webproc release settings
ENV WEBPROC_VERSION 0.2.2
ENV GIT_URL https://github.com/jpillora/webproc/releases
ENV WEBPROC_URL $GIT_URL/download/$WEBPROC_VERSION/webproc_linux_amd64.gz
# fetch dnsmasq and webproc binary
RUN apk update \
    && apk --no-cache add dnsmasq libcap \
    && apk add --no-cache --virtual .build-deps curl \
    && curl -sL $WEBPROC_URL | gzip -d - > /usr/local/bin/webproc \
    && chmod +x /usr/local/bin/webproc \
    && apk del .build-deps
#configure dnsmasq
RUN mkdir -p /etc/default/
RUN echo -e "ENABLED=1\nIGNORE_RESOLVCONF=yes" > /etc/default/dnsmasq
COPY dnsmasq.conf /etc/dnsmasq.conf


#run!
ENTRYPOINT ["webproc","--config","/etc/dnsmasq.conf", \
            "--","/usr/sbin/dnsmasq","--no-daemon"]
