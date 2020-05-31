# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

REGISTRY_URI=${REGISTRY}
EXTRA_ARGS+= --build-arg REGISTRY_URI=${REGISTRY_URI}
EXTRA_ARGS+= --build-arg LABEL=${LABEL}
EXTRA_ARGS+= --build-arg WATCHTOWER_CMD="${WATCHTOWER_CMD}"
EXTRA_ARGS+= --build-arg SSH_PORT="${SSH_PORT}"

all: protoc rpcserver compose autotest-lucifer autotest-gwt autotest \
	db devserver ssp offloader envoy remote_access ui remote_agent \
        remote-scheduler local-dev remote-access

#TODO refactor the common rules into a single rule.

rpcserver: export DOCKER_BUILDKIT=1
rpcserver:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-rpcserver:${LABEL} -f \
		dockerfiles/rpcserver/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab-rpcserver:${LABEL}

compose: export DOCKER_BUILDKIT=1
compose:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-compose:${LABEL} \
		-f dockerfiles/compose/Dockerfile dockerfiles/compose
	docker push ${REGISTRY_URI}/moblab-compose:${LABEL}

autotest: autotest-afe autotest-dbsetup autotest-monitor \
	autotest-host autotest-abort

autotest-base: export DOCKER_BUILDKIT=1
autotest-base:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-base:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.base ..
	docker push ${REGISTRY_URI}/moblab-autotest-base:${LABEL}

autotest-afe: export DOCKER_BUILDKIT=1
autotest-afe: autotest-base
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-afe:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.afe dockerfiles/autotest
	docker push ${REGISTRY_URI}/moblab-autotest-afe:${LABEL}

autotest-dbsetup: export DOCKER_BUILDKIT=1
autotest-dbsetup: autotest-base
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-dbsetup:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.dbsetup dockerfiles/autotest
	docker push ${REGISTRY_URI}/moblab-autotest-dbsetup:${LABEL}

protoc: export DOCKER_BUILDKIT=1
protoc:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/protoc:${LABEL} \
		-f dockerfiles/utilities/Dockerfile.protoc dockerfiles/utilities
	docker push ${REGISTRY_URI}/protoc:${LABEL}

autotest-lucifer: export DOCKER_BUILDKIT=1
autotest-lucifer:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-lucifer:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.lucifer dockerfiles/autotest
	docker push ${REGISTRY_URI}/moblab-autotest-lucifer:${LABEL}

autotest-gwt: export DOCKER_BUILDKIT=1
autotest-gwt:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-gwt:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.gwt ..
	docker push ${REGISTRY_URI}/moblab-autotest-gwt:${LABEL}

autotest-monitor: export DOCKER_BUILDKIT=1
autotest-monitor: autotest-base
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-monitor_db:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.monitor_db dockerfiles/autotest
	docker push ${REGISTRY_URI}/moblab-autotest-monitor_db:${LABEL}

autotest-host: export DOCKER_BUILDKIT=1
autotest-host: autotest-base
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-host:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.hostscheduler dockerfiles/autotest
	docker push ${REGISTRY_URI}/moblab-autotest-host:${LABEL}

autotest-abort: export DOCKER_BUILDKIT=1
autotest-abort: autotest-base
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-aborter:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.job_aborter dockerfiles/autotest
	docker push ${REGISTRY_URI}/moblab-autotest-aborter:${LABEL}

db: export DOCKER_BUILDKIT=1
db:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-db:${LABEL} \
		-f dockerfiles/db/Dockerfile dockerfiles/db
	docker push ${REGISTRY_URI}/moblab-db:${LABEL}
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-db-init:${LABEL} \
		-f dockerfiles/db/Dockerfile.db_init dockerfiles/db
	docker push ${REGISTRY_URI}/moblab-db-init:${LABEL}

devserver: export DOCKER_BUILDKIT=1
devserver:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/devserver:${LABEL} \
		-f dockerfiles/devserver/Dockerfile dockerfiles/devserver
	docker push ${REGISTRY_URI}/devserver:${LABEL}

ui: export DOCKER_BUILDKIT=1
ui:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-ui:${LABEL} \
		-f dockerfiles/ui/Dockerfile .
	docker push ${REGISTRY_URI}/moblab-ui:${LABEL}

ssp: export DOCKER_BUILDKIT=1
ssp:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-ssp:${LABEL} \
		-f dockerfiles/ssp/Dockerfile dockerfiles/ssp
	docker push ${REGISTRY_URI}/moblab-ssp:${LABEL}

offloader: export DOCKER_BUILDKIT=1
offloader:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-offloader:${LABEL} \
		-f dockerfiles/offloader/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab-offloader:${LABEL}

envoy: export DOCKER_BUILDKIT=1
envoy:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/envoy-proxy:${LABEL} \
		-f dockerfiles/envoy/Dockerfile dockerfiles/envoy
	docker push ${REGISTRY_URI}/envoy-proxy:${LABEL}

remote-access: export DOCKER_BUILDKIT=1
remote-access:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/remote_access:${LABEL} \
		-f dockerfiles/remote_access/Dockerfile dockerfiles/remote_access
	docker push ${REGISTRY_URI}/remote_access:${LABEL}

watchtower: export DOCKER_BUILDKIT=1
watchtower:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/watchtower:${LABEL} \
		-f dockerfiles/watchtower/Dockerfile dockerfiles/watchtower
	docker push ${REGISTRY_URI}/watchtower:${LABEL}

local-dev: export DOCKER_BUILDKIT=1
local-dev:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-dev-environment:${LABEL} \
		-f dockerfiles/local-dev-environment/Dockerfile.base dockerfiles/local-dev-environment
	docker push ${REGISTRY_URI}/moblab-dev-environment:${LABEL}

remote-agent: export DOCKER_BUILDKIT=1
remote-agent:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-remote-agent:${LABEL} -f \
		dockerfiles/remote_agent/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab-remote-agent:${LABEL}

remote-scheduler: export DOCKER_BUILDKIT=1
remote-scheduler:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-remote-scheduler:${LABEL} -f \
		dockerfiles/remote-scheduler/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab-remote-scheduler:${LABEL}

gwtcompiler: export DOCKER_BUILDKIT=1
gwtcompiler:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/gwtcompiler:${LABEL} \
		-f dockerfiles/utilities/Dockerfile.gwtcompiler dockerfiles/utilities
	docker push ${REGISTRY_URI}/gwtcompiler:${LABEL}

.PHONY: rpcserver compose db autotest devserver ui ssp offloader envoy remote_access remote_agent remote-scheduler gwtcompiler
