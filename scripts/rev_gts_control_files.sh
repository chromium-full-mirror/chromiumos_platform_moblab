#!/bin/bash

# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Usage rev_gts_control_files.sh 6.0_r1-4868992 $HOME/gts-6.0_r1-4868992.zip
# where 6.0_r1-4868992 is the version of GTS you want to update to and
# $HOME/gts-6.0_r1-4868992.zip is the full path to the zip file downloaded from
# https://support.google.com/androidpartners_gms/answer/6173316

set -x
set -e

GTS_VERSION="${1}"
GTS_BINARY="${2}"
GTS_BUCKET_LOCATION="gs://chromeos-partner-gts/"
GTS_FILE="${GTS_BUCKET_LOCATION}"android-gts-"${GTS_VERSION}".zip

gsutil cp "${GTS_BINARY}"  gs://chromeos-partner-gts/
LAST_GTS_BINARY=$(gsutil ls -r gs://chromeos-partner-gts/ | tail -1)
rm -f update_acl_setting
gsutil acl get "${LAST_GTS_BINARY}" > update_acl_setting
gsutil acl set update_acl_setting "${GTS_FILE}"

THIRD_PARTY="${HOME}"/trunk/src/third_party
AUTO_TEST_LOCATION="${THIRD_PARTY}"/autotest/files/server/site_tests
CHEETS_PRIVATE_LOCATION="${THIRD_PARTY}"/autotest-tests-cheets/server/site_tests

# Sync the two repos that matter
cd "${CHEETS_PRIVATE_LOCATION}"
repo sync .

#Start a new repo branch
cd "${AUTO_TEST_LOCATION}"/cheets_GTS
repo start uprev_"${GTS_VERSION}"
repo sync .


# Set up path so it can access adb and aapt
# TODO - follow the href in
# https://dl.google.com/android/repository/platform-tools-latest-linux.zip
# to get the latest platform tools version
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip -P /tmp
unzip -o /tmp/platform-tools_r27.0.1-linux.zip -d /tmp
PATH=${PATH}:/tmp/platform-tools

# Remove / Move all the existing control files - except for the
# control.tradefed-run-collect-tests-only
rm -f control.*.G*

# Generate the new control files
"${CHEETS_PRIVATE_LOCATION}"/cheets_GTS/generate_controlfiles.py \
    "${GTS_FILE}" --is_public

# Edit cheets_GTS.py,
# Change the _PARTNER_GTS_LOCATION  to have the correct version of the GTS zip
sed -E s#"^_PARTNER_GTS_LOCATION = _PARTNER_GTS_BUCKET \+ .*$"#"_PARTNER_GTS_LOCATION = _PARTNER_GTS_BUCKET \+ 'gts-${GTS_VERSION}.zip'"# -i $(pwd)/"cheets_GTS.py"

git add . -A

#Submit the CL for review
git commit -F- <<EOF
[autotest] Uprev GTS version to ${GTS_VERSION}

TEST=None
BUG=b:68021674
EOF

repo upload . --verify

