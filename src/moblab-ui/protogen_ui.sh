#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set +x

# This script should be run from moblab_common directory

echo "Running Angular protogen"

moblab_ui_dir="$(dirname "$(readlink -f "$0")")"
cd $moblab_ui_dir

mkdir -p ./proto_js

# temporary until we move all protos into protos directory
mkdir -p ./protos_temp
cp ../*/*.proto protos_temp/
cp ../moblab_common/protos/*.proto protos_temp/

# TODO: parametrize docker image for local dev 
docker run --rm \
    -v `pwd`:/protoc/volume \
    gcr.io/chromeos-partner-moblab/protoc:autopush \
    bash -c "protoc \
    -I=/protoc/volume/protos_temp/ \
    -I=/protoc/include/ \
    --experimental_allow_proto3_optional \
    --js_out=import_style=commonjs:/protoc/volume/src/app/services/ \
    --grpc-web_out=import_style=commonjs+dts,mode=grpcwebtext:/protoc/volume/src/app/services/ \
    /protoc/volume/protos_temp/moblabrpc.proto \
    /protoc/volume/protos_temp/moblab_configuration_rpc.proto \
    google/protobuf/empty.proto \
    google/protobuf/any.proto"

rm -dr ./protos_temp
