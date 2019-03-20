#!/bin/bash

# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Usage rev_cts_control_files.sh 7.1_r16
# where 7.1_r16 is the version of CTS you want to update to.

set -x
set -e

CTS_LETTER="Instant"
CTS_VERSION="${1}"
DOWNLOAD_LOCATION="https://dl.google.com/dl/android/cts/"
X86_FILE="${DOWNLOAD_LOCATION}"/android-cts_instant-"${CTS_VERSION}"-linux_x86-x86.zip
ARM_FILE="${DOWNLOAD_LOCATION}"/android-cts_instant-"${CTS_VERSION}"-linux_x86-arm.zip

THIRD_PARTY="${HOME}"/trunk/src/third_party
AUTO_TEST_LOCATION="${THIRD_PARTY}"/autotest/files/server/site_tests

CHEETS_PRIVATE_LOCATION="${THIRD_PARTY}"/autotest-tests-cheets/server/site_tests

# Sync the two repos that matter
cd "${CHEETS_PRIVATE_LOCATION}"
repo start "uprev_private_${CTS_VERSION}_${CTS_LETTER}"
repo sync .

#Start a new repo branch
mkdir -p "${AUTO_TEST_LOCATION}/cheets_CTS_${CTS_LETTER}"
cd "${AUTO_TEST_LOCATION}/cheets_CTS_${CTS_LETTER}"
repo start "uprev_${CTS_VERSION}_${CTS_LETTER}"
repo sync .


# Set up path so it can access adb and aapt
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip -P /tmp
unzip -o /tmp/platform-tools-latest-linux.zip -d /tmp
PATH=${PATH}:/tmp/platform-tools

# Remove / Move all the existing control files - except for the
# control.tradefed-run-collect-tests-only
rm -f control.*.C*
rm -f *vm-tests-tf

# Generate the new control files
"${CHEETS_PRIVATE_LOCATION}"/cheets_CTS_${CTS_LETTER}/generate_controlfiles.py \
  "${X86_FILE}" \
  "${ARM_FILE}" \
  --is_public

git add . -A

#Submit the CL for review
git commit -F- <<EOF
[autotest] Uprev CTS ${CTS_LETTER} version to ${CTS_VERSION}

TEST=None
BUG=b:68778082
EOF

repo upload . --verify --wip 

# Edit cheets_CTS_${CTS_LETTER}.py,
cd "${CHEETS_PRIVATE_LOCATION}/cheets_CTS_${CTS_LETTER}"
# Change the _PUBLIC_CTS dict to have the correct version of the CTS zip
sed -E s#".*arm.*_PUBLIC_CTS.*$"#"    \'arm\': _PUBLIC_CTS + 'android-cts_instant-"${CTS_VERSION}"-linux_x86-arm.zip',"# -i $(pwd)/"cheets_CTS_${CTS_LETTER}.py"
sed -E s#".*x86.*_PUBLIC_CTS.*$"#"    \'x86\': _PUBLIC_CTS + 'android-cts_instant-"${CTS_VERSION}"-linux_x86-x86.zip',"# -i $(pwd)/"cheets_CTS_${CTS_LETTER}.py"

git add . -A

#Submit the CL for review
git commit -F- <<EOF
[autotest] Uprev CTS ${CTS_LETTER} version to ${CTS_VERSION}

TEST=None
BUG=b:68778082
EOF

repo upload . --verify --wip

