# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

######################################################################

FROM ${REGISTRY_URI}/moblab_common:${LABEL} as common

######################################################################

FROM ${BASE_REGISTRY_URI}/python:3.8-slim-buster

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

RUN apt-get update && apt-get install -yq \
    cmake \
    curl \
    gcc-multilib \
    gnupg \
    libssl-dev \
    nmap \
    unzip \
    zlib1g-dev

# Install the google cloud sdk
RUN echo \
    "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
    http://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg  \
    add - && apt-get update -y && apt-get install google-cloud-sdk -y

RUN rm -rf /usr/lib/google-cloud-sdk/bin/anthoscli \
           /usr/lib/google-cloud-sdk/bin/kuberun

COPY --chown=moblab src/dockerfiles/rpcserver/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /wheels
COPY --from=common /wheel/*py3* .
RUN pip install *.whl
RUN rm -rf /wheels

RUN mkdir /var/log/moblab

# Installs Moblab API client library
WORKDIR /tmp/moblab_api_client_library
RUN curl https://storage.googleapis.com/moblab-api-distribution/google-chromeos-moblab.tar.gz -o google-chromeos-moblab.tar.gz
RUN tar -xvzf google-chromeos-moblab.tar.gz
RUN python3 -m pip install .
RUN rm -rf /tmp/moblab_api_client_library

RUN apt purge -yq unzip cmake libssl-dev zlib1g-dev curl gcc-multilib
RUN apt autoremove -yq
RUN apt-get clean

# Need to be in docker group to use docker API
RUN addgroup --gid 412 docker
RUN usermod -aG docker moblab

COPY --chown=moblab src/moblab_rpcserver/ /etc/moblab/moblab_rpcserver

WORKDIR /moblab
USER moblab

EXPOSE 6002

CMD ["/etc/moblab/moblab_rpcserver/rpcserver.py"]
