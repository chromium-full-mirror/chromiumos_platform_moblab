#!/bin/sh
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

# This script assumes an $LABEL is set of autopush/beta/release or a custom label
# for development

SERVICE=${1}
VERSION=${2}

echo "service: ${SERVICE} version: ${VERSION}"
if [ ${VERSION} ]
then
    sed -i.bak s/${SERVICE}=autopush/${SERVICE}=${VERSION}/g main.env
fi
