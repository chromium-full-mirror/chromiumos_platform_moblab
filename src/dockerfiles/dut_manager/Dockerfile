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

ARG UID=246

RUN addgroup --gid $UID moblab && adduser --ingroup moblab --uid $UID \
    --disabled-password --gecos "" moblab

COPY --chown=moblab dut_manager/ /etc/moblab/dut_manager
COPY --from=protos /protos /etc/moblab/dut_manager

COPY --chown=moblab dockerfiles/dut_manager/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /var/log/moblab
RUN chown moblab:moblab /var/log/moblab

WORKDIR /etc/moblab/dut_manager
USER moblab

CMD ["python", "dut_manager.py"]
