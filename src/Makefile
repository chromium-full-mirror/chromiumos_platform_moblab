export LABEL := ${USER}
export REGISTRY := us-docker.pkg.dev/chromeos-partner-moblab-dev/$(subst .,,${USER})
export BUILD_VERSION := ${LABEL}
export BASE_REGISTRY_URI := us-docker.pkg.dev/chromeos-partner-moblab-dev/base-containers
WATCHTOWER_CMD := --enable-lifecycle-hooks --interval 60 --include-restarting
SSH_PORT := 22
E2E_TARGET_URL := http://localhost:80/
UID := 246
GID := 412

-include local_registry.mk
include common.mk
