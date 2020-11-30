#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set +x

# This script should be run from moblab_common directory

echo "Running protogen"

moblab_common_dir="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
cd $moblab_common_dir

mkdir -p moblab_common/proto

# temporary until we move all protos into protos directory
mkdir -p protos_temp/moblab_common/proto
cp ./*/*.proto protos_temp/moblab_common/proto/
cp moblab_common/protos/*.proto protos_temp/moblab_common/proto/

# TODO: parametrize docker image for local dev 
docker run --rm \
    -v `pwd`:/protoc/volume \
    gcr.io/chromeos-partner-moblab/protoc:autopush \
    bash -c "/protoc/protoc \
    -I=/protoc/volume/protos_temp/ \
    -I=/protoc/include/ \
    --experimental_allow_proto3_optional \
    --python_out=:/protoc/volume/ \
    --grpc_python_out=:/protoc/volume/ \
    --plugin=protoc-gen-grpc_python=/protoc/grpc_python_plugin \
    /protoc/volume/protos_temp/moblab_common/proto/*.proto"

rm -dr protos_temp

touch moblab_common/proto/__init__.py
