# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=autopush

######################################################################

FROM ${REGISTRY_URI}/moblab_common:${LABEL} as common

######################################################################

FROM ${BASE_REGISTRY_URI}/python:3.8-slim-buster

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab


COPY --chown=moblab src/remote-scheduler/ /etc/moblab/remote-scheduler

RUN apt-get update && apt-get install -yq \
    cmake \
    curl \
    fping \
    libssl-dev \
    unzip \
    zlib1g-dev

COPY --chown=moblab src/dockerfiles/rpcserver/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /wheel
COPY --from=common /wheel/*py3* .
RUN pip install *.whl
RUN rm -rf /wheels

RUN mkdir /var/log/moblab

RUN apt purge -yq unzip cmake libssl-dev zlib1g-dev curl
RUN apt autoremove -yq
RUN apt-get clean

WORKDIR /moblab
USER moblab

CMD ["/etc/moblab/remote-scheduler/moblab_remote_scheduler.py", "-v"]
