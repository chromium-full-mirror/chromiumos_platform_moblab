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

COPY --chown=moblab inventory/ /etc/moblab/inventory
COPY --from=protos /protos /etc/moblab/inventory

COPY --chown=moblab dockerfiles/inventory/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /var/log/moblab
RUN chown moblab:moblab /var/log/moblab

WORKDIR /etc/moblab/inventory
USER moblab

CMD ["python", "inventory.py"]
