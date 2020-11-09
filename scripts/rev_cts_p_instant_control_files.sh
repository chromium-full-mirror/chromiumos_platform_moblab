#!/bin/bash

# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Usage rev_cts_control_files.sh 7.1_r16
# where 7.1_r16 is the version of CTS you want to update to.

set -x
set -e

CTS_LETTER="Instant"
BUG_NUMBER=68778082
QUALIFIED_CTS_VERSION="_instant-${1}"
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/rev_cts_control_files_common.sh"
