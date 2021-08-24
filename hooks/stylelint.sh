#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -e

pwd=$(pwd)
moblab_ui=src/moblab-ui
files=$(python $pwd/hooks/find_files.py -e .html .scss .css -i /mobmonitor-ui/)

if [ ! -d "$pwd/$moblab_ui/node_modules/stylelint" ]
then
    echo "stylelint library is missing, please run npm install in ${moblab_ui}"
    exit 1
fi

if [ ! -z "$files" ]
then
    cd $moblab_ui
    npx stylelint --fix ${files}
    echo "${files}" | xargs git add
    # Run lint for issues that could not be fixed above.
    npx stylelint ${files}
fi