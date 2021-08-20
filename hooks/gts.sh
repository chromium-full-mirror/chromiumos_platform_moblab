#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -e

pwd=$(pwd)
moblab_ui=src/moblab-ui
files=$(python $pwd/hooks/find_files.py -e .ts -i /mobmonitor-ui/)

if [ ! -d "$pwd/$moblab_ui/node_modules/gts" ]
then
    echo "gts library is missing, please run npm install in ${moblab_ui}"
    exit 1
fi

if [ ! -z "$files" ]
then
    cd $moblab_ui
    gts fix ${files}
    echo "${files}" | xargs git add
    # Run lint for issues that could not be fixed above.
    gts lint ${files}
fi