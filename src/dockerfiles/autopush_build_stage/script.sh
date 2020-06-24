# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -x

git clone https://chromium.googlesource.com/chromiumos/platform/moblab
cd moblab
git checkout ${BRANCH_NAME}
git pull

gcloud auth activate-service-account source-code-sync@chromeos-partner-moblab.iam.gserviceaccount.com --key-file=/root/auth/auth.json
git remote add google https://source.developers.google.com/p/chromeos-partner-moblab/r/${REPO_NAME}
git push -f google ${BRANCH_NAME}
