# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

######################################################################
# Python 3 build stage

FROM ${BASE_REGISTRY_URI}/python:3.8-buster as python3-build

WORKDIR /src/tools/
COPY src/tools/create-moblab-id.py .

WORKDIR /src/moblab_common
COPY src/moblab_common/ .

RUN mkdir /test
RUN mv test/ /

COPY src/dockerfiles/moblab_common/setup.py /
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel
RUN python3 /setup.py bdist_wheel

WORKDIR /wheel
RUN cp /src/moblab_common/dist/* .

######################################################################
# Python 2 build stage

FROM ${BASE_REGISTRY_URI}/python:2-buster as python2-build

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

######################################################################
# Unit testing stage

FROM python3-build as python3-test

# Installs Moblab API client library
WORKDIR /tmp/moblab_api_client_library
RUN curl https://storage.googleapis.com/moblab-api-distribution/google-chromeos-moblab.tar.gz -o google-chromeos-moblab.tar.gz
RUN tar -xvzf google-chromeos-moblab.tar.gz
RUN python3 -m pip install .
RUN rm -rf /tmp/moblab_api_client_library

WORKDIR /test
RUN python3 -m pip install /src/moblab_common/dist/*.whl

RUN rm -rf /src

######################################################################
# Wheel package distribution stage

FROM ${BASE_REGISTRY_URI}/debian:buster-slim

WORKDIR /wheel

COPY --from=python3-build /wheel/* .
COPY --from=python2-build /wheel/* .
