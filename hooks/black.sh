#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -e

pwd=$(pwd)
files=$(python $pwd/hooks/find_py_files.py)

if [ ! -z "$files" ]
then
    black --line-length=79 ${files}
    # Add back the modified/prettified files to staging
    echo "${files}" | xargs git add
fi
