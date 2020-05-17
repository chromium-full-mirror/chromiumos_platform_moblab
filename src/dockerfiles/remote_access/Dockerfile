# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

###########################################################

FROM docker:latest as docker

###########################################################

FROM ${REGISTRY_URI}/moblab-autotest-base:${LABEL} as autotest

###########################################################

FROM linuxserver/openssh-server:latest

COPY ./testing_rsa.pub /
COPY --from=docker /usr/local/bin/docker /usr/local/bin/docker

RUN apk add --no-cache --upgrade openssh-client

RUN mkdir -p /home/moblab
RUN mkdir -p /home/moblab/.ssh
COPY --from=autotest /chromite/ssh_keys/* /home/moblab/.ssh/
RUN chmod -R 600 /home/moblab/.ssh/*

RUN echo "chown \"\$USER_NAME\":\"\$USER_NAME\" /home/\"\$USER_NAME\"" >> /etc/cont-init.d/10-adduser
RUN echo "export \$HOME=/home/\"\$USER_NAME\"" >> /etc/cont-init.d/10-adduser
RUN echo "addgroup --gid 412 docker" >> /etc/cont-init.d/10-adduser
RUN echo "usermod -aG docker moblab" >> /etc/cont-init.d/10-adduser

#RUN echo "LogLevel DEBUG3" >> /etc/ssh/sshd_config