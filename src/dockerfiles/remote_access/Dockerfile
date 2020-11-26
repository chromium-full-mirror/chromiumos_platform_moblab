# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

###########################################################

FROM ${REGISTRY_URI}/moblab_common:${LABEL} as common

###########################################################

FROM ${BASE_REGISTRY_URI}/docker:latest as docker

###########################################################

FROM ${REGISTRY_URI}/moblab-autotest-base:${LABEL} as autotest

###########################################################

FROM ${BASE_REGISTRY_URI}/linuxserver/openssh-server:latest

COPY src/dockerfiles/remote_access/testing_rsa.pub /
COPY --from=docker /usr/local/bin/docker /usr/local/bin/docker

RUN apk add --no-cache --upgrade \
    openssh-client \
    python3 \
    python3-dev \
    py3-setuptools \
    alpine-sdk \
    linux-headers \
    gcc \
    cmake \
    openssl-dev \
    zlib-dev \
    libffi-dev \
    py-pip \
    libstdc++

COPY src/dockerfiles/remote_access/requirements.txt ./
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

RUN mkdir -p /home/moblab
RUN mkdir -p /home/moblab/.ssh
COPY --from=autotest /chromite/ssh_keys/* /home/moblab/.ssh/
RUN chmod -R 600 /home/moblab/.ssh/*

WORKDIR /wheels
COPY --from=common /wheel/*py3* .
RUN pip install *.whl
RUN rm -rf /wheels

RUN apk del \
    python3-dev \
    py3-setuptools \
    alpine-sdk \
    linux-headers \
    gcc \
    cmake \
    openssl-dev \
    zlib-dev \
    libffi-dev

RUN echo "chown \"\$USER_NAME\":\"\$USER_NAME\" /home/\"\$USER_NAME\"" >> /etc/cont-init.d/10-adduser
RUN echo "export \$HOME=/home/\"\$USER_NAME\"" >> /etc/cont-init.d/10-adduser
RUN echo "addgroup --gid 412 docker" >> /etc/cont-init.d/10-adduser
RUN echo "usermod -aG docker moblab" >> /etc/cont-init.d/10-adduser

COPY src/dockerfiles/remote_access/fix_ping.sh /
RUN chmod u+x /fix_ping.sh
WORKDIR /etc/services.d/fix_ping
COPY src/dockerfiles/remote_access/fix_ping.run ./run

COPY src/tools/reboot /usr/local/bin
COPY src/tools/factory_reset /usr/local/bin
COPY src/tools/host_command.py /usr/local/bin
RUN chmod uog+x /usr/local/bin/reboot
RUN chmod uog+x /usr/local/bin/factory_reset

WORKDIR /var/log

#RUN echo "LogLevel DEBUG3" >> /etc/ssh/sshd_config
