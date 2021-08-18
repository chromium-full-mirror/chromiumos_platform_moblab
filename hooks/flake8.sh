#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -e

pwd=$(pwd)
files=$(python $pwd/hooks/find_files.py -e .py)
if [ ! -z "$files" ]
then
    flake8 ${files} || true
fi
