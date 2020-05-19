# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

######################################################################

FROM ${REGISTRY_URI}/protoc:${LABEL} as protoc

######################################################################

FROM python:3.8-buster as proto_build

WORKDIR /
COPY --from=protoc /protoc/* /usr/local/bin
COPY third_party/autotest/tko/tko.proto /usr/local/autotest/tko/tko.proto
RUN protoc --proto_path /usr/local/autotest/tko \
    --python_out=/usr/local/autotest/tko \
    /usr/local/autotest/tko/tko.proto

####################################################################

FROM python:3.8-slim-buster

WORKDIR /

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab
RUN apt-get update && apt-get install -yq sudo vim
RUN echo "moblab     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN usermod -aG sudo moblab

COPY --chown=moblab ./src/moblab_common /moblab/src/moblab_common
COPY --chown=moblab ./src/tools /moblab/src/tools
COPY --chown=moblab ./src/dockerfiles /moblab/src/dockerfiles
COPY --chown=moblab ./src/host_services /moblab/src/host_services
COPY --chown=moblab ./setup.py /moblab/
COPY --chown=moblab --from=proto_build /usr/local/autotest /usr/local/autotest

COPY src/dockerfiles/offloader/requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

WORKDIR /moblab
RUN python ./setup.py install

WORKDIR /etc/moblab/moblab_results_uploader
COPY --chown=moblab src/moblab_results_uploader/ /etc/moblab/moblab_results_uploader

RUN mkdir -p /var/log/moblab/offloader
RUN chown -R moblab /var/log/moblab

RUN apt-get clean

COPY --chown=moblab src/dockerfiles/offloader/start_offloader.sh /
RUN chmod uog+rx /start_offloader.sh

USER moblab

CMD ["/start_offloader.sh"]
