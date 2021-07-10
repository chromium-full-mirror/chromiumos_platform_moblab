#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set +x

# !!! This script is executed by protoc docker container

echo "Running Angular protogen"

cd /workspace/src/moblab-ui

# temporary until we move all protos into protos directory
mkdir -p protos_temp
cp ../*/*.proto protos_temp/
cp ../moblab_common/protos/*.proto protos_temp/

protoc \
    -I=/workspace/src/moblab-ui/protos_temp/ \
    -I=/protoc/include/ \
    --experimental_allow_proto3_optional \
    --js_out=import_style=commonjs:/workspace/src/moblab-ui/src/app/services/ \
    --grpc-web_out=import_style=commonjs+dts,mode=grpcwebtext:/workspace/src/moblab-ui/src/app/services/ \
    /workspace/src/moblab-ui/protos_temp/moblabrpc.proto \
    /workspace/src/moblab-ui/protos_temp/moblab_configuration_rpc.proto \
    google/protobuf/duration.proto \
    google/protobuf/empty.proto \
    google/protobuf/any.proto

rm -dr protos_temp
