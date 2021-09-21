# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=autopush

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

WORKDIR /install
RUN cp /src/moblab_common/dist/* .
COPY src/dockerfiles/moblab_common/install.sh .

######################################################################
# Unit testing stage

FROM python3-build as python3-test

# Installs Moblab API client library
WORKDIR /tmp/moblab_api_client_library
RUN curl https://storage.googleapis.com/moblab-api-distribution/python-client-library/google-chromeos-moblab-python-1.3.0-beta.tar.gz -o google-chromeos-moblab-python-1.3.0-beta.tar.gz
RUN tar -xvzf google-chromeos-moblab-python-1.3.0-beta.tar.gz
RUN python3 -m pip install .
RUN rm -rf /tmp/moblab_api_client_library

WORKDIR /test
RUN python3 -m pip install /src/moblab_common/dist/*.whl

RUN rm -rf /src

######################################################################
# Wheel package distribution stage

FROM ${BASE_REGISTRY_URI}/debian:buster-slim

WORKDIR /install

COPY --from=python3-build /install/* .
