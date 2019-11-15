# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

all:

install:
	install -m 0644 -D -t ${DESTDIR}etc/moblab/moblab_results_uploader \
		*.py \
		test_results_uploading_filter.yaml
	install -t ${DESTDIR}etc/moblab/moblab_results_uploader \
		moblab_results_uploader
