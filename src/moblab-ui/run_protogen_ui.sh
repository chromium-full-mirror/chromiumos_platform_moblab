#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set +x

# This script should be run from moblab_common directory

echo "Running Angular protogen"

moblab_dir="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
echo "cd $moblab_dir"
cd $moblab_dir

if [ -z "${SOURCE_ROOT}" ]
then
    SOURCE_ROOT=$(pwd)
fi

if [ -z "${REGISTRY}" ]
then
    REGISTRY=gcr.io/chromeos-partner-moblab
fi

if [ -z "${LABEL}" ]
then
    LABEL=autopush
fi

docker run --rm \
-v ${SOURCE_ROOT}:/workspace \
${REGISTRY}/protoc:${LABEL} \
bash /workspace/src/moblab-ui/protogen_ui.sh
