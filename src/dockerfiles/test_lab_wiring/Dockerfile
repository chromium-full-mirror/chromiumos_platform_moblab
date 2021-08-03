# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=autopush

######################################################################

FROM ${REGISTRY_URI}/infra-protos:${LABEL} as protos

######################################################################

FROM ${BASE_REGISTRY_URI}/python:3.8-slim-buster

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

WORKDIR /etc/moblab/test_lab_wiring
COPY --chown=moblab test_lab_wiring/ .
COPY --from=protos /protos .

WORKDIR /etc/moblab/test_lab_wiring
COPY --chown=moblab dockerfiles/test_lab_wiring/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /var/log/moblab
RUN chown moblab:moblab /var/log/moblab
USER moblab

CMD ["python", "test_lab_wiring.py", "-v"]
