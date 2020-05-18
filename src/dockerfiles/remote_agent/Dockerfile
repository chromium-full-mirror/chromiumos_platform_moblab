# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG ${REGISTRY_URI}

######################################################################

FROM gcr.io/chromeos-partner-moblab/protoc:release as protoc

######################################################################

FROM python:3.8-buster as build

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

WORKDIR /etc/moblab/remote_agent

COPY --from=protoc /protoc/* /usr/local/bin/
COPY src/remote_agent/ /etc/moblab/remote_agent
RUN protoc -I=/etc/moblab/remote_agent \
    --python_out=:/etc/moblab/remote_agent \
    --grpc_python_out=:/etc/moblab/remote_agent \
    --plugin=protoc-gen-grpc_python=/usr/local/bin/grpc_python_plugin \
    remoteagentrpc.proto

######################################################################

FROM python:3.8-slim-buster

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

COPY --chown=moblab --from=build /etc/moblab/remote_agent \
    /etc/moblab/remote_agent

RUN apt-get update && apt-get install -yq \
    mariadb-client

COPY --chown=moblab src/dockerfiles/remote_agent/requirements.txt ./
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

WORKDIR /moblab
USER moblab

EXPOSE 6050

CMD ["/etc/moblab/remote_agent/server.py", "-v"]
