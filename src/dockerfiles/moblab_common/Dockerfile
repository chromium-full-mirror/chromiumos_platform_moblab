# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

######################################################################

FROM ${REGISTRY_URI}/protoc:${LABEL} as protoc

######################################################################

FROM ${BASE_REGISTRY_URI}/python:3.8-buster as python3

WORKDIR /src/tools/
COPY src/tools/create-moblab-id.py .

WORKDIR /src/moblab_common
COPY src/moblab_common/ .

COPY src/dockerfiles/moblab_common/setup.py /
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel
RUN python3 /setup.py bdist_wheel

WORKDIR /wheel
RUN cp /src/moblab_common/dist/* .

######################################################################

FROM ${BASE_REGISTRY_URI}/python:2-buster as python2

WORKDIR /src/tools/
COPY src/tools/create-moblab-id.py .

WORKDIR /src/moblab_common
COPY src/moblab_common/ .


COPY src/dockerfiles/moblab_common/setup.py /
RUN python2 -m pip install --upgrade pip
RUN python2 -m pip install --upgrade setuptools wheel
RUN python2 /setup.py bdist_wheel

WORKDIR /wheel
RUN ls /src/moblab_common/
RUN cp /src/moblab_common/dist/* .
#RUN rm -rf /src

######################################################################

FROM ${BASE_REGISTRY_URI}/debian:buster-slim

WORKDIR /wheel

COPY --from=python3 /wheel/* .
COPY --from=python2 /wheel/* .
