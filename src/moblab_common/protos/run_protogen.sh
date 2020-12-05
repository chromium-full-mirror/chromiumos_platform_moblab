#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set +x

echo "Running docker protogen"

moblab_dir="$(dirname "$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")")"
echo "cd $moblab_dir"
cd $moblab_dir

docker run --rm \
    -v `pwd`:/protoc/volume \
    gcr.io/chromeos-partner-moblab/protoc:autopush \
    bash /protoc/volume/src/moblab_common/protos/protogen.sh
