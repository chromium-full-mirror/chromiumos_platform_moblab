# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

######################################################################

FROM ${REGISTRY_URI}/protoc:${LABEL} as protoc

######################################################################

FROM python:3.8-buster as python3

WORKDIR /src/tools/
COPY src/tools/create-moblab-id.py .

WORKDIR /src/moblab_common
COPY src/moblab_common/ .

# copy protoc binaries
COPY --from=protoc /protoc/* /usr/local/bin/

# dir for all proto files 
RUN mkdir -p ./proto/moblab_common/proto/

# copy protoc from across all projects 
COPY src/*/*.proto proto/moblab_common/proto/
RUN cp -r ./protos/* proto/moblab_common/proto/
COPY --from=protoc /protoc/include/ proto/moblab_common/proto/
RUN touch ./proto/__init__.py

RUN protoc \
    -I=/src/moblab_common/proto/ \
    -I=/usr/local/bin \
    --experimental_allow_proto3_optional \
    --python_out=:/src/moblab_common/proto/ \
    --grpc_python_out=:/src/moblab_common/proto/ \
    --plugin=protoc-gen-grpc_python=/usr/local/bin/grpc_python_plugin \
    /src/moblab_common/proto/moblab_common/proto/*.proto \
    /usr/local/bin/google/protobuf/empty.proto \
    /usr/local/bin/google/protobuf/any.proto

RUN cp -r proto/moblab_common/proto/* ./proto/
RUN touch ./proto/google/__init__.py
RUN touch ./proto/google/protobuf/__init__.py

#RUN rm -rf /src/moblab_common/proto/moblab_common

COPY src/dockerfiles/moblab_common/setup.py /
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel
RUN python3 /setup.py bdist_wheel

WORKDIR /wheel
RUN cp /src/moblab_common/dist/* .

######################################################################

FROM python:2-buster as python2

WORKDIR /src/tools/
COPY src/tools/create-moblab-id.py .

WORKDIR /src/moblab_common
COPY src/moblab_common/ .

COPY --from=protoc /protoc/* /usr/local/bin/
RUN mkdir -p ./proto/moblab_common/proto/
COPY src/*/*.proto ./proto/moblab_common/proto/
RUN touch ./proto/__init__.py

RUN protoc -I=/src/moblab_common/proto/ \
    --experimental_allow_proto3_optional \
    --python_out=:/src/moblab_common/proto/ \
    --grpc_python_out=:/src/moblab_common/proto/ \
    --plugin=protoc-gen-grpc_python=/usr/local/bin/grpc_python_plugin \
    /src/moblab_common/proto/moblab_common/proto/*.proto

RUN cp proto/moblab_common/proto/*.py ./proto/

COPY src/dockerfiles/moblab_common/setup.py /
RUN python2 -m pip install --upgrade pip
RUN python2 -m pip install --upgrade setuptools wheel
RUN python2 /setup.py bdist_wheel

WORKDIR /wheel
RUN ls /src/moblab_common/
RUN cp /src/moblab_common/dist/* .
#RUN rm -rf /src

######################################################################

FROM debian:buster-slim

WORKDIR /wheel

COPY --from=python3 /wheel/* .
COPY --from=python2 /wheel/* .
