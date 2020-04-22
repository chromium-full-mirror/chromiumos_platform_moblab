# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

BASE_URL=gcr.io/chromeos-partner-moblab

all: rpcserver compose autotest db devserver ssp offloader ui envoy remote_access

#TODO refactor the common rules into a single rule.

rpcserver: export DOCKER_BUILDKIT=1
rpcserver:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/moblab-rpcserver:${LABEL} -f \
		dockerfiles/rpcserver/Dockerfile ..
	docker push ${BASE_URL}/moblab-rpcserver:${LABEL}

compose: export DOCKER_BUILDKIT=1
compose:
	cp dockerfiles/compose/docker-compose.yaml.${LABEL} dockerfiles/compose/docker-compose.yaml
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/moblab-compose:${LABEL} \
		-f dockerfiles/compose/Dockerfile dockerfiles/compose
	docker push ${BASE_URL}/moblab-compose:${LABEL}

autotest: export DOCKER_BUILDKIT=1
autotest:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/moblab-autotest:${LABEL} \
		-f dockerfiles/autotest/Dockerfile ..
	docker push ${BASE_URL}/moblab-autotest:${LABEL}

db: export DOCKER_BUILDKIT=1
db:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/moblab-db:${LABEL} \
		-f dockerfiles/db/Dockerfile dockerfiles/db
	docker push ${BASE_URL}/moblab-db:${LABEL}
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/moblab-db-init:${LABEL} \
		-f dockerfiles/db/Dockerfile.db_init dockerfiles/db
	docker push ${BASE_URL}/moblab-db-init:${LABEL}

devserver: export DOCKER_BUILDKIT=1
devserver:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/devserver:${LABEL} \
		-f dockerfiles/devserver/Dockerfile dockerfiles/devserver
	docker push ${BASE_URL}/devserver:${LABEL}

ui: export DOCKER_BUILDKIT=1
ui:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/moblab-ui:${LABEL} \
		-f dockerfiles/ui/Dockerfile .
	docker push ${BASE_URL}/moblab-ui:${LABEL}

ssp: export DOCKER_BUILDKIT=1
ssp:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/moblab-ssp:release \
		-f dockerfiles/ssp/Dockerfile dockerfiles/ssp
	docker push ${BASE_URL}/moblab-ssp:release

offloader: export DOCKER_BUILDKIT=1
offloader:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/moblab-offloader:${LABEL} \
		-f dockerfiles/offloader/Dockerfile ..
	docker push ${BASE_URL}/moblab-offloader:${LABEL}

envoy: export DOCKER_BUILDKIT=1
envoy:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/envoy-proxy:${LABEL} \
		-f dockerfiles/envoy/Dockerfile dockerfiles/envoy
	docker push ${BASE_URL}/envoy-proxy:${LABEL}

remote_access: export DOCKER_BUILDKIT=1
remote_access:
	docker build ${EXTRA_ARGS} -t ${BASE_URL}/remote_access:${LABEL} \
		-f dockerfiles/remote_access/Dockerfile dockerfiles/remote_access
	docker push ${BASE_URL}/remote_access:${LABEL}

.PHONY: rpcserver compose db autotest devserver ui ssp offloader envoy remote_access
