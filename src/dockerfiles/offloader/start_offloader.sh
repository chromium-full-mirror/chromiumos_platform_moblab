#!/bin/bash
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

/etc/moblab/moblab_results_uploader/moblab_results_uploader \
-l /var/log/moblab/offloader.log \
--uploading-filter-config-file /etc/moblab/moblab_results_uploader/test_results_uploading_filter.yaml \
run \
--credentials-file /home/moblab/.service_account.json \
--min-age-to-upload 0 \
--timeout-days 3 \
--min-age-to-prune 3 \
--jobs 30
