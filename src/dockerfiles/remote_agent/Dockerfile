# Copyright 2019 The Chromium OS Authors. All rights reserved.
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

COPY --chown=moblab src/remote_agent/ /etc/moblab/remote_agent

RUN apt-get update && apt-get install -yq \
    mariadb-client \
    libssl-dev \
    zlib1g-dev \
    gcc-multilib \
    cmake \
    curl \
    gnupg \
    sudo

COPY --chown=moblab src/dockerfiles/remote_agent/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install the google cloud sdk
RUN echo \
    "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
    http://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg  \
    add - && apt-get update -y && apt-get install google-cloud-sdk -y

RUN pip install --upgrade google-cloud-pubsub

RUN DEBIAN_FRONTEND='noninteractive' apt-get -y install nmap

RUN pip install pyyaml

RUN sudo apt-get -y install gcc python3-dev
RUN sudo pip3 install psutil

WORKDIR /wheels
COPY --from=common /wheel/*py3* .
RUN pip install *.whl
RUN rm -rf /wheels

RUN apt purge -yq cmake libssl-dev zlib1g-dev gcc-multilib
RUN apt autoremove -yq
RUN apt-get clean

RUN mkdir /moblab
RUN mkdir /var/log/moblab
RUN chown -R moblab /moblab
RUN chown -R moblab /var/log/moblab

WORKDIR /moblab
USER moblab

EXPOSE 6050

CMD ["/etc/moblab/remote_agent/server.py", "-v"]
