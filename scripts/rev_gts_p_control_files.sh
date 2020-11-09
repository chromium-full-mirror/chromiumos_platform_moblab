#!/bin/bash

# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Usage rev_gts_control_files.sh 6.0_r1-4868992 $HOME/gts-6.0_r1-4868992.zip
# where 6.0_r1-4868992 is the version of GTS you want to update to and
# $HOME/gts-6.0_r1-4868992.zip is the full path to the zip file downloaded from
# https://support.google.com/androidpartners_gms/answer/6173316

set -x
set -e

GTS_DIRNAME="cheets_GTS"
GTS_TEST_FILENAME="cheets_GTS.py"
BUG_NUMBER=68021674

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/rev_gts_control_files_common.sh"
