# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# This makefile is just used to make development easier

BASE_URL=gcr.io/chromeos-partner-moblab

all: rpcserver compose autotest db devserver ui offloader

rpcserver: export DOCKER_BUILDKIT=1
rpcserver:
	docker build -t ${BASE_URL}/moblab-rpcserver:${USER} -f \
		dockerfiles/rpcserver/Dockerfile .
	docker push ${BASE_URL}/moblab-rpcserver:${USER}

compose: export DOCKER_BUILDKIT=1
compose:
	cp dockerfiles/compose/docker-compose.yaml.${USER} dockerfiles/compose/docker-compose.yaml
	docker build -t ${BASE_URL}/moblab-compose:${USER} \
		-f dockerfiles/compose/Dockerfile dockerfiles/compose
	docker push ${BASE_URL}/moblab-compose:${USER}

autotest: export DOCKER_BUILDKIT=1
autotest:
	docker build -t ${BASE_URL}/moblab-autotest:${USER} \
		-f dockerfiles/autotest/Dockerfile ..
	docker push ${BASE_URL}/moblab-autotest:${USER}

db: export DOCKER_BUILDKIT=1
db:
	docker build -t ${BASE_URL}/moblab-db:${USER} \
		-f dockerfiles/db/Dockerfile dockerfiles/db
	docker push ${BASE_URL}/moblab-db:${USER}
	docker build -t ${BASE_URL}/moblab-db-init:${USER} \
		-f dockerfiles/db/Dockerfile.db_init dockerfiles/db
	docker push ${BASE_URL}/moblab-db-init:${USER}

devserver: export DOCKER_BUILDKIT=1
devserver:
	docker build -t ${BASE_URL}/devserver:${USER} \
		-f dockerfiles/devserver/Dockerfile dockerfiles/devserver
	docker push ${BASE_URL}/devserver:${USER}

ui: export DOCKER_BUILDKIT=1
ui:
	docker build -t ${BASE_URL}/moblab-ui:${USER} \
		-f dockerfiles/ui/Dockerfile .
	docker push ${BASE_URL}/moblab-ui:${USER}

ssp: export DOCKER_BUILDKIT=1
ssp:
	docker build -t ${BASE_URL}/moblab-ssp:release \
		-f dockerfiles/ssp/Dockerfile dockerfiles/ssp
	docker push ${BASE_URL}/moblab-ssp:release

offloader: export DOCKER_BUILDKIT=1
offloader:
	docker build -t ${BASE_URL}/moblab-offloader:${USER} \
		-f dockerfiles/offloader/Dockerfile ..
	docker push ${BASE_URL}/moblab-offloader:${USER}


.PHONY: rpcserver compose db autotest devserver ui ssp offloader
