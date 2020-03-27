# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

#############
### build ###
#############

# base image
FROM python:3.8-buster as build

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab


# install protoc
ENV PROTOBUF_URL https://github.com/protocolbuffers/protobuf/releases/download/v3.10.0/protoc-3.10.0-linux-x86_64.zip
RUN curl -L -o /tmp/protobuf.zip $PROTOBUF_URL
WORKDIR /tmp/
RUN unzip protobuf.zip
RUN cp bin/protoc /usr/local/bin

# install grpc_python_plugin
RUN git clone https://github.com/grpc/grpc.git
WORKDIR /tmp/grpc
RUN git submodule update --init
RUN make grpc_python_plugin
RUN cp /tmp/grpc/bins/opt/grpc_python_plugin /usr/local/bin

# set working directory
WORKDIR /etc/moblab/moblab-rpcserver

COPY src/moblab-rpcserver/ /etc/moblab/moblab-rpcserver
RUN protoc -I=/etc/moblab/moblab-rpcserver \
    --python_out=:/etc/moblab/moblab-rpcserver \
    --grpc_python_out=:/etc/moblab/moblab-rpcserver \
    --plugin=protoc-gen-grpc_python=/usr/local/bin/grpc_python_plugin \
    moblabrpc.proto

############
### prod ###
############

# base image
FROM python:3-buster

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab
# copy artifact build from the 'build environment'
COPY --chown=moblab --from=build /etc/moblab/moblab-rpcserver /etc/moblab/moblab-rpcserver
RUN apt-get update && apt-get install -yq unzip cmake libssl-dev fping

COPY --chown=moblab src/dockerfiles/rpcserver/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# moblab_common
COPY --chown=moblab ./src/moblab_common /moblab/src/moblab_common
COPY --chown=moblab ./src/tools /moblab/src/tools
COPY --chown=moblab ./src/dockerfiles /moblab/src/dockerfiles
COPY --chown=moblab ./src/host_services /moblab/src/host_services
COPY --chown=moblab ./setup.py /moblab/

WORKDIR /moblab
RUN python ./setup.py install

RUN mkdir /var/log/moblab

RUN apt purge -yq unzip cmake libssl-dev
RUN apt-get clean

USER moblab

EXPOSE 6002

CMD ["/etc/moblab/moblab-rpcserver/moblab-rpcserver.py", "-v"]
