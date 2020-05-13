#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

/etc/moblab/moblab_results_uploader/moblab_results_uploader \
      -l /var/log/moblab/offloader.log \
      run \
      --credentials-file /home/moblab/.service_account.json \
      --min-age-to-prune 1 \
      --jobs 100
