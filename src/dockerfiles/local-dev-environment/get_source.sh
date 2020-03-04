#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

if [ ! -d  depot_tools ]; then
  git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
fi

export PATH=$(pwd)/depot_tools:${PATH}

repo init -u https://chrome-internal.googlesource.com/chromeos/manifest-internal.git \
          --repo-url https://chromium.googlesource.com/external/repo.git \
          -g moblab
repo sync -j4
