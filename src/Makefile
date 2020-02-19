# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# This makefile is just used to make development easier

BASE_URL="gcr.io/chromeos-partner-moblab"

rpcserver: export DOCKER_BUILDKIT=1
rpcserver:
	docker build -t ${BASE_URL}/moblab-rpcserver:${USER} -f \
		dockerfiles/rpcserver/Dockerfile .
	docker push ${BASE_URL}/moblab-rpcserver:${USER}

compose: export DOCKER_BUILDKIT=1
compose:
	docker build -t ${BASE_URL}/moblab-compose:${USER} \
		-f dockerfiles/compose/Dockerfile dockerfiles/compose
	docker push ${BASE_URL}/moblab-compose:${USER}

.PHONY: rpcserver compose
