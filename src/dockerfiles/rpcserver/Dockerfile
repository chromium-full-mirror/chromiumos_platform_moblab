# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

#############
### build ###
#############

# base image
FROM python:3.6-stretch as build

RUN apt-get update && apt-get install -yq unzip cmake

COPY dockerfiles/rpcserver/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

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

COPY moblab-rpcserver/ /etc/moblab/moblab-rpcserver
RUN protoc -I=/etc/moblab/moblab-rpcserver \
    --python_out=:/etc/moblab/moblab-rpcserver \
    --grpc_python_out=:/etc/moblab/moblab-rpcserver \
    --plugin=protoc-gen-grpc_python=/usr/local/bin/grpc_python_plugin \
    moblabrpc.proto

# moblab_common
WORKDIR /moblab_common
COPY moblab_common/ .
RUN cp setup.py /
RUN python /setup.py install

# run tests

# generate build
#RUN ng build --output-path=dist

############
### prod ###
############

# base image
FROM python:3.6-slim

# copy artifact build from the 'build environment'
COPY --from=build /etc/moblab/moblab-rpcserver /etc/moblab/moblab-rpcserver
COPY --from=build /usr/local/lib/python3.6/site-packages \
    /usr/local/lib/python3.6/site-packages

RUN mkdir /var/log/moblab
# run moblab-rpcserver

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

EXPOSE 6002

CMD ["/etc/moblab/moblab-rpcserver/moblab-rpcserver.py", "-v"]
