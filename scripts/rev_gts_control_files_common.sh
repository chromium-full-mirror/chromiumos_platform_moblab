# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x
set -e

GTS_VERSION="${1}"
GTS_BINARY="${2}"
GTS_BUCKET_LOCATION="gs://chromeos-partner-gts/"
GTS_PACKAGE_FILENAME="gts-${GTS_VERSION}.zip"
GTS_PACKAGE_BUCKET_LOCATION="${GTS_BUCKET_LOCATION}${GTS_PACKAGE_FILENAME}"

gsutil -m cp "${GTS_BINARY}" "${GTS_PACKAGE_BUCKET_LOCATION}"
gsutil cp gs://chromeos-partner-gts/update_acl_setting /tmp
gsutil acl set /tmp/update_acl_setting "${GTS_PACKAGE_BUCKET_LOCATION}"

AUTO_TEST_LOCATION="/autotest/server/site_tests"

#Start a new branch
cd "${AUTO_TEST_LOCATION}/${GTS_DIRNAME}"
git checkout master
git pull
git rebase
git checkout -b "uprev_${GTS_DIRNAME}_${GTS_VERSION}"
git branch --set-upstream-to=origin/master "uprev_${GTS_DIRNAME}_${GTS_VERSION}"
git pull
git rebase

# Set up path so it can access adb and aapt
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip -P /tmp
unzip -o /tmp/platform-tools-latest-linux.zip -d /tmp
PATH=${PATH}:/tmp/platform-tools

# Remove / Move all the existing control files - except for the
# control.tradefed-run-collect-tests-only
rm -f control.G*

# Generate the new control files
"${AUTO_TEST_LOCATION}/${GTS_DIRNAME}"/generate_controlfiles.py \
    "${GTS_PACKAGE_BUCKET_LOCATION}" --is_public

# Edit cheets_GTS.py,
# Change the _PARTNER_GTS_LOCATION  to have the correct version of the GTS zip
sed -E s#"^_PARTNER_GTS_LOCATION = _PARTNER_GTS_BUCKET \+ .*$"#"_PARTNER_GTS_LOCATION = _PARTNER_GTS_BUCKET \+ '${GTS_PACKAGE_FILENAME}'"# -i $(pwd)/"${GTS_TEST_FILENAME}"

f=`git rev-parse --git-dir`/hooks/commit-msg ; mkdir -p $(dirname $f) ; curl -Lo $f https://gerrit-review.googlesource.com/tools/hooks/commit-msg ; chmod +x $f
git add . -A
git cl format --no-clang-format
git add . -A

git add . -A

#Submit the CL for review
git commit -F- <<EOF
[autotest] Uprev GTS version to ${GTS_VERSION}

BUG=b:${BUG_NUMBER}
TEST=None
EOF

git push origin HEAD:refs/for/master
