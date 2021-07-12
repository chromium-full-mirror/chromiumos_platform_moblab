# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

REGISTRY_URI=${REGISTRY}
EXTRA_ARGS+= --build-arg REGISTRY_URI=${REGISTRY_URI}
EXTRA_ARGS+= --build-arg LABEL=${LABEL}
EXTRA_ARGS+= --build-arg WATCHTOWER_CMD="${WATCHTOWER_CMD}"
EXTRA_ARGS+= --build-arg SSH_PORT="${SSH_PORT}"
EXTRA_ARGS+= --build-arg BASE_REGISTRY_URI="${BASE_REGISTRY_URI}"


all:	autotest \
		compose \
		common \
		db \
		devserver \
		dut_manager \
		dut_manager_storage \
		moblab-db-setup \
		dhcp \
		dns \
		envoy \
		logrotate \
		mobmonitor \
		offloader \
		remote-access\
		remote-agent \
		remote-scheduler \
		rpcserver \
		ssp \
		ui \
		watchtower

#TODO refactor the common rules into a single rule.

rpcserver: export DOCKER_BUILDKIT=1
rpcserver: common
	docker build ${EXTRA_ARGS} --label "version=${BUILD_VERSION}"  \
		-t ${REGISTRY_URI}/moblab-rpcserver:${LABEL} \
		-f dockerfiles/rpcserver/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab-rpcserver:${LABEL}

compose: export DOCKER_BUILDKIT=1
compose:
	docker build ${EXTRA_ARGS} --label "version=${BUILD_VERSION}" \
		-t ${REGISTRY_URI}/moblab-compose:${LABEL} \
		-f dockerfiles/compose/Dockerfile dockerfiles/compose
	docker push ${REGISTRY_URI}/moblab-compose:${LABEL}

autotest: autotest-afe autotest-dbsetup autotest-monitor \
	autotest-host autotest-lucifer autotest-abort

autotest-base: export DOCKER_BUILDKIT=1
autotest-base: protoc common chromite
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
autotest-lucifer: protoc
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-autotest-lucifer:${LABEL} \
		-f dockerfiles/autotest/Dockerfile.lucifer dockerfiles/autotest
	docker push ${REGISTRY_URI}/moblab-autotest-lucifer:${LABEL}

autotest-monitor: export DOCKER_BUILDKIT=1
autotest-monitor: autotest-base autotest-lucifer
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
devserver: chromite
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/devserver:${LABEL} \
		-f dockerfiles/devserver/Dockerfile dockerfiles/devserver
	docker push ${REGISTRY_URI}/devserver:${LABEL}

ui: export DOCKER_BUILDKIT=1
ui: protoc
	./moblab-ui/run_protogen_ui.sh
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-ui:${LABEL} \
		-f dockerfiles/ui/Dockerfile .
	docker push ${REGISTRY_URI}/moblab-ui:${LABEL}

ssp: export DOCKER_BUILDKIT=1
ssp: chromite
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-ssp:${LABEL} \
		-f dockerfiles/ssp/Dockerfile dockerfiles/ssp
	docker push ${REGISTRY_URI}/moblab-ssp:${LABEL}

offloader: export DOCKER_BUILDKIT=1
offloader: protoc common
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-offloader:${LABEL} \
		-f dockerfiles/offloader/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab-offloader:${LABEL}

envoy: export DOCKER_BUILDKIT=1
envoy:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/envoy-proxy:${LABEL} \
		-f dockerfiles/envoy/Dockerfile dockerfiles/envoy
	docker push ${REGISTRY_URI}/envoy-proxy:${LABEL}

remote-access: export DOCKER_BUILDKIT=1
remote-access: autotest-base common
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/remote_access:${LABEL} \
		-f dockerfiles/remote_access/Dockerfile ..
	docker push ${REGISTRY_URI}/remote_access:${LABEL}

watchtower: export DOCKER_BUILDKIT=1
watchtower:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/watchtower:${LABEL} \
		-f dockerfiles/watchtower/Dockerfile dockerfiles/watchtower
	docker push ${REGISTRY_URI}/watchtower:${LABEL}

remote-agent: export DOCKER_BUILDKIT=1
remote-agent: common
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-remote-agent:${LABEL} -f \
		dockerfiles/remote_agent/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab-remote-agent:${LABEL}

remote-scheduler: export DOCKER_BUILDKIT=1
remote-scheduler: common
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-remote-scheduler:${LABEL} -f \
		dockerfiles/remote-scheduler/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab-remote-scheduler:${LABEL}

mobmonitor: export DOCKER_BUILDKIT=1
mobmonitor: common
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/mobmonitor:${LABEL} \
		-f dockerfiles/mobmonitor/Dockerfile ..
	docker push ${REGISTRY_URI}/mobmonitor:${LABEL}

dhcp: export DOCKER_BUILDKIT=1
dhcp:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-dhcp:${LABEL} \
		-f dockerfiles/dhcp/Dockerfile dockerfiles/dhcp
	docker push ${REGISTRY_URI}/moblab-dhcp:${LABEL}

dns: export DOCKER_BUILDKIT=1
dns:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-dns:${LABEL} \
		-f dockerfiles/dns/Dockerfile dockerfiles/dns
	docker push ${REGISTRY_URI}/moblab-dns:${LABEL}

common: export DOCKER_BUILDKIT=1
common: protoc
	./moblab_common/protos/run_protogen.sh
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab_common:${LABEL} \
		-f dockerfiles/moblab_common/Dockerfile ..
	docker push ${REGISTRY_URI}/moblab_common:${LABEL}

moblab-db-setup: export DOCKER_BUILDKIT=1
moblab-db-setup:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/moblab-db-setup:${LABEL} \
		-f dockerfiles/moblab_common/Dockerfile.dbsetup .
	docker push ${REGISTRY_URI}/moblab-db-setup:${LABEL}

logrotate: export DOCKER_BUILDKIT=1
logrotate:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/logrotate:${LABEL} \
		-f dockerfiles/utilities/Dockerfile.logrotate dockerfiles/utilities
	docker push ${REGISTRY_URI}/logrotate:${LABEL}

chromite: export DOCKER_BUILDKIT=1
chromite:
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/chromite:${LABEL} \
		-f dockerfiles/utilities/Dockerfile.chromite dockerfiles/utilities
	docker push ${REGISTRY_URI}/chromite:${LABEL}

dut-manager: export DOCKER_BUILDKIT=1
dut-manager: infra-protos
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/dut-manager:${LABEL} \
		-f dockerfiles/dut_manager/Dockerfile .
	docker push ${REGISTRY_URI}/dut-manager:${LABEL}

dut-manager-storage: export DOCKER_BUILDKIT=1
dut-manager-storage: infra-protos common
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/dut-manager-storage:${LABEL} \
		-f dockerfiles/dut_manager_storage/Dockerfile .
	docker push ${REGISTRY_URI}/dut-manager-storage:${LABEL}

infra-protos: export DOCKER_BUILDKIT=1
infra-protos: protoc
	docker build ${EXTRA_ARGS} -t ${REGISTRY_URI}/infra-protos:${LABEL} \
		-f dockerfiles/utilities/Dockerfile.infra_protos dockerfiles/utilities
	docker push ${REGISTRY_URI}/infra-protos:${LABEL}




moblab:	autotest \
		common \
		compose \
		db \
		devserver \
		moblab-db-setup \
		local-dev \
		mobmonitor \
		offloader \
		remote-access \
		remote-agent \
		remote-scheduler \
		rpcserver \
		ui

misc:	dhcp \
		dns \
		envoy \
		logrotate \
		ssp \
		watchtower

# Run moblab db revision autogen
moblab-db-revision: REVISION_NAME="$(shell read -p "Revision name: " rev_name; echo $$rev_name)"
moblab-db-revision:
	docker build ${EXTRA_ARGS} --build-arg USER=${USER} --build-arg USERID=$(shell id -u) -t moblab-db-revision:${LABEL} \
		-f dockerfiles/moblab_common/Dockerfile.dbrevision .
	docker run -it -v `pwd`/moblab_common:/workdir/moblab_common \
		--network default_moblab moblab-db-revision:${LABEL} $(REVISION_NAME)


# Build & run, but don't push
test-rpcserver: export DOCKER_BUILDKIT=1
test-rpcserver: rpcserver
	install -d -m 0777 moblab_rpcserver/coverage
	docker run -w /etc/moblab/moblab_rpcserver -v "${PWD}/moblab_rpcserver/coverage":/etc/moblab/moblab_rpcserver/coverage --rm ${REGISTRY_URI}/moblab-rpcserver:${LABEL} \
		bash -c 'coverage run -m unittest discover -p "*_unittest.py" && coverage html -d coverage --omit "*_unittest.py"'

# Change to run in a container
test-moblab-ui: export DOCKER_BUILDKIT=1
test-moblab-ui: moblab-ui

test-common: export DOCKER_BUILDKIT=1
test-common:
	./moblab_common/protos/run_protogen.sh
	docker build ${EXTRA_ARGS} -t moblab_common_test_py3:${LABEL} \
		--target python3-test -f dockerfiles/moblab_common/Dockerfile ..

	docker run -it moblab_common_test_py3:${LABEL} \
		bash -c 'python3 -m unittest discover -p "*_unittest.py" -v /test/'

test:	test-rpcserver \
		test-common
