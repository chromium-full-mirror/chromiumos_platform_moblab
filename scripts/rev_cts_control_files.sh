#!/bin/bash

# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Usage rev_cts_control_files.sh 7.1_r16
# where 7.1_r16 is the version of CTS you want to update to.

set -x
set -e

CTS_VERSION="${1}"
DOWNLOAD_LOCATION="https://dl.google.com/dl/android/cts"
X86_FILE="${DOWNLOAD_LOCATION}"/android-cts-"${CTS_VERSION}"-linux_x86-x86.zip
ARM_FILE="${DOWNLOAD_LOCATION}"/android-cts-"${CTS_VERSION}"-linux_x86-arm.zip

THIRD_PARTY="${HOME}"/trunk/src/third_party
AUTO_TEST_LOCATION="${THIRD_PARTY}"/autotest/files/server/site_tests

CHEETS_PRIVATE_LOCATION="${THIRD_PARTY}"/autotest-tests-cheets/server/site_tests

# Sync the two repos that matter
cd "${CHEETS_PRIVATE_LOCATION}"
repo sync .
cd "${AUTO_TEST_LOCATION}"/cheets_CTS_N
repo sync .

#Start a new repo branch
repo start uprev_"${CTS_VERSION}"

# Set up path so it can access adb and aapt
# TODO - follow the href in
# https://dl.google.com/android/repository/platform-tools-latest-linux.zip
# to get the latest platform tools version
curl https://dl.google.com/android/repository/platform-tools_r27.0.1-linux.zip \
  -o /tmp/platform-tools_r27.0.1-linux.zip
unzip -o /tmp/platform-tools_r27.0.1-linux.zip -d /tmp
PATH=${PATH}:/tmp/platform-tools

# Remove / Move all the existing control files - except for the
# control.tradefed-run-collect-tests-only
rm control.*.C*;rm *vm-tests-tf

# Generate the new control files
"${CHEETS_PRIVATE_LOCATION}"/cheets_CTS_N/generate_controlfiles.py \
  "${ARM_FILE}" \
  "${X86_FILE}"

# Edit cheets_CTS_N.py,
# Change the _CTS_URI dict to have the correct version of the CTS zip
sed -E s#".*arm.*_DL_CTS.*$"#"    \'arm\': _DL_CTS + 'android-cts-"${CTS_VERSION}"-linux_x86-arm.zip',"# -i $(pwd)/"cheets_CTS_N.py"

sed -E s#".*x86.*_DL_CTS.*$"#"    \'x86\': _DL_CTS + 'android-cts-"${CTS_VERSION}"-linux_x86-x86.zip',"# -i $(pwd)/"cheets_CTS_N.py"

git add . -A

#Submit the CL for review
git commit -F- <<EOF
[autotest] Uprev CTS version to ${CTS_VERSION}

TEST=None
BUG=b:68778082
EOF

repo upload . --verify -d

