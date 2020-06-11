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

RUN pip3 install --upgrade pip setuptools
RUN pip3 install six wheel

RUN mkdir -p /home/moblab
RUN mkdir -p /home/moblab/.ssh
COPY --from=autotest /chromite/ssh_keys/* /home/moblab/.ssh/
RUN chmod -R 600 /home/moblab/.ssh/*

COPY --chown=moblab ./src/moblab_common /moblab/src/moblab_common
COPY --chown=moblab ./src/tools /moblab/src/tools
COPY --chown=moblab ./src/host_services /moblab/src/host_services
COPY --chown=moblab ./setup.py /moblab/
WORKDIR /moblab
RUN python3 ./setup.py install

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

COPY src/tools/reboot /usr/local/bin
COPY src/tools/factory_reset /usr/local/bin
COPY src/tools/host_command.py /usr/local/bin
RUN chmod uog+x /usr/local/bin/reboot
RUN chmod uog+x /usr/local/bin/factory_reset

#RUN echo "LogLevel DEBUG3" >> /etc/ssh/sshd_config