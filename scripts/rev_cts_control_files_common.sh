# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x
set -e

CTS_VERSION="${1}"
DOWNLOAD_LOCATION="https://dl.google.com/dl/android/cts/"
X86_FILE="${DOWNLOAD_LOCATION}"/android-cts"${QUALIFIED_CTS_VERSION}"-linux_x86-x86.zip
ARM_FILE="${DOWNLOAD_LOCATION}"/android-cts"${QUALIFIED_CTS_VERSION}"-linux_x86-arm.zip

AUTO_TEST_LOCATION="${THIRD_PARTY}"/autotest/files/server/site_tests
AUTO_TEST_LOCATION=/autotest/server/site_tests

#Start a new branch
cd "${AUTO_TEST_LOCATION}/cheets_CTS_${CTS_LETTER}"
git checkout main
git pull
git rebase
git checkout -b "uprev_${CTS_VERSION}_${CTS_LETTER}"
git branch --set-upstream-to=origin/main "uprev_${CTS_VERSION}_${CTS_LETTER}"
git pull
git rebase


# Set up path so it can access adb and aapt
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip -P /tmp
unzip -o /tmp/platform-tools-latest-linux.zip -d /tmp
PATH=${PATH}:/tmp/platform-tools

# Remove / Move all the existing control files - except for the
# control.tradefed-run-collect-tests-only
rm -f control.arm.C*
rm -f control.x86.C*
rm -f contol.x86*vm-tests-tf
rm -f control.arm*vm-tests-tf

# Generate the new control files
"${AUTO_TEST_LOCATION}"/cheets_CTS_${CTS_LETTER}/generate_controlfiles.py \
  "${X86_FILE}" \
  "${ARM_FILE}" \
  --is_public

# Edit cheets_CTS_${CTS_LETTER}.py,
cd "${AUTO_TEST_LOCATION}/cheets_CTS_${CTS_LETTER}"
# Change the _PUBLIC_CTS dict to have the correct version of the CTS zip
sed -E s#".*arm.*_PUBLIC_CTS.*$"#"    \'arm\': _PUBLIC_CTS + 'android-cts"${QUALIFIED_CTS_VERSION}"-linux_x86-arm.zip',"# -i $(pwd)/"cheets_CTS_${CTS_LETTER}.py"
sed -E s#".*x86.*_PUBLIC_CTS.*$"#"    \'x86\': _PUBLIC_CTS + 'android-cts"${QUALIFIED_CTS_VERSION}"-linux_x86-x86.zip',"# -i $(pwd)/"cheets_CTS_${CTS_LETTER}.py"

f=`git rev-parse --git-dir`/hooks/commit-msg ; mkdir -p $(dirname $f) ; curl -Lo $f https://gerrit-review.googlesource.com/tools/hooks/commit-msg ; chmod +x $f
git add . -A
git cl format --no-clang-format
git add . -A

#Submit the CL for review
git commit -F- <<EOF
[autotest] Uprev CTS ${CTS_LETTER} version to ${CTS_VERSION}

BUG=b:${BUG_NUMBER}
TEST=None
EOF

git push origin HEAD:refs/for/main
