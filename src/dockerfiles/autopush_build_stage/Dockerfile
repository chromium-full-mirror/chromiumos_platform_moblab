# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM gcr.io/google.com/cloudsdktool/cloud-sdk

ARG BRANCH_NAME
ARG REPO_NAME

WORKDIR /
COPY script.sh /

ENTRYPOINT ["sh", "/script.sh"]