#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set +x

# !!! This script is executed by protoc docker container

echo "Running protogen inside protoc container"

cd /protoc/volume/src

mkdir -p moblab_common/proto

# temporary until we move all protos into protos directory
mkdir -p protos_temp/moblab_common/proto
cp ./*/*.proto protos_temp/moblab_common/proto/
cp moblab_common/protos/*.proto protos_temp/moblab_common/proto/
cp ../os-dependent/common/*.proto protos_temp/moblab_common/proto/


protoc \
    -I=/protoc/volume/src/protos_temp/ \
    -I=/protoc/include/ \
    --experimental_allow_proto3_optional \
    --python_out=:/protoc/volume/src/ \
    --grpc_python_out=:/protoc/volume/src/ \
    --plugin=protoc-gen-grpc_python=/protoc/grpc_python_plugin \
    /protoc/volume/src/protos_temp/moblab_common/proto/*.proto

rm -dr protos_temp

touch moblab_common/proto/__init__.py
