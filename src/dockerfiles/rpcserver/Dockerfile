# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

######################################################################

FROM ${REGISTRY_URI}/protoc:${LABEL} as protoc

######################################################################

FROM python:3.8-buster as build

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

WORKDIR /etc/moblab/moblab-rpcserver

COPY --from=protoc /protoc/* /usr/local/bin/
COPY src/moblab-rpcserver/ /etc/moblab/moblab-rpcserver
RUN protoc -I=/etc/moblab/moblab-rpcserver \
    --python_out=:/etc/moblab/moblab-rpcserver \
    --grpc_python_out=:/etc/moblab/moblab-rpcserver \
    --plugin=protoc-gen-grpc_python=/usr/local/bin/grpc_python_plugin \
    moblabrpc.proto

######################################################################

FROM python:3.8-slim-buster

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

COPY --chown=moblab --from=build /etc/moblab/moblab-rpcserver \
    /etc/moblab/moblab-rpcserver
RUN apt-get update && apt-get install -yq \
    cmake \
    curl \
    fping \
    libssl-dev \
    unzip \
    zlib1g-dev \
    libcap2-bin

COPY --chown=moblab src/dockerfiles/rpcserver/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# moblab_common
COPY --chown=moblab ./src/moblab_common /moblab/src/moblab_common
COPY --chown=moblab ./src/tools /moblab/src/tools
COPY --chown=moblab ./src/host_services /moblab/src/host_services
COPY --chown=moblab ./setup.py /moblab/

WORKDIR /moblab
RUN python -m pip install .

RUN rm -rf /moblab

RUN mkdir /var/log/moblab

# Installs Moblab API client library
WORKDIR /tmp/moblab_api_client_library
RUN curl https://storage.googleapis.com/moblab-api-distribution/google-chromeos-moblab.tar.gz -o google-chromeos-moblab.tar.gz
RUN tar -xvzf google-chromeos-moblab.tar.gz
RUN python -m pip install .
RUN rm -rf /tmp/moblab_api_client_library

RUN setcap cap_net_raw+ep /usr/bin/fping

RUN apt purge -yq unzip cmake libssl-dev zlib1g-dev curl zlib1g-dev
RUN apt-get clean

# Need to be in docker group to use docker API
RUN addgroup --gid 412 docker
RUN usermod -aG docker moblab

WORKDIR /moblab
USER moblab

EXPOSE 6002

CMD ["/etc/moblab/moblab-rpcserver/moblab-rpcserver.py", "-v"]
