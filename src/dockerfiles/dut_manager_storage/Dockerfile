# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=autopush

######################################################################

FROM gcr.io/chromeos-partner-moblab/infra_protos:haddowk as protos

######################################################################

######################################################################

FROM ${REGISTRY_URI}/moblab_common:${LABEL} as common

######################################################################

FROM ${BASE_REGISTRY_URI}/python:3.8-slim-buster

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

# Needed for dut_connector
RUN apt-get update && apt-get install -yq nmap

WORKDIR /etc/moblab/dut_manager_storage
COPY --chown=moblab dut_manager_storage/*.py .
COPY --from=protos /protos .

WORKDIR /wheels
COPY --from=common /wheel/*py3* .
RUN pip install *.whl
RUN rm -rf /wheels

WORKDIR /etc/moblab/dut_manager_storage
COPY --chown=moblab dockerfiles/dut_manager_storage/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Need to be in docker group to use docker API
RUN addgroup --gid 412 docker
RUN usermod -aG docker moblab

RUN mkdir -p /var/log/moblab
RUN chown moblab:moblab /var/log/moblab
USER moblab

CMD ["python", "dut_manager_storage.py", "-v"]
