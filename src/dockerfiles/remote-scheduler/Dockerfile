# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL

######################################################################

FROM gcr.io/chromeos-partner-moblab/protoc:${LABEL} as protoc

######################################################################

FROM python:3.8-buster as build

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

WORKDIR /etc/moblab/remote-scheduler

COPY --from=protoc /protoc/* /usr/local/bin/
COPY src/remote-scheduler/ /etc/moblab/remote-scheduler
RUN protoc -I=/etc/moblab/remote-scheduler \
    --python_out=:/etc/moblab/remote-scheduler \
    moblab_request.proto

######################################################################

FROM python:3.8-slim-buster

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

COPY --chown=moblab --from=build /etc/moblab/remote-scheduler \
    /etc/moblab/remote-scheduler

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

# moblab_common
COPY --chown=moblab ./src/moblab_common /moblab/src/moblab_common
COPY --chown=moblab ./src/tools /moblab/src/tools
COPY --chown=moblab ./src/host_services /moblab/src/host_services
COPY --chown=moblab ./setup.py /moblab/

WORKDIR /moblab
RUN python -m pip install .

RUN rm -rf /moblab

RUN mkdir /var/log/moblab

RUN apt purge -yq unzip cmake libssl-dev zlib1g-dev curl
RUN apt-get clean

WORKDIR /moblab
USER moblab

CMD ["/etc/moblab/remote-scheduler/moblab_remote_scheduler.py", "-v"]
