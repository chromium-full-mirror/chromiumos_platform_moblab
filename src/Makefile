export LABEL=${USER}
export REGISTRY=gcr.io/chromeos-partner-moblab
export BUILD_VERSION=${LABEL}
WATCHTOWER_CMD=--enable-lifecycle-hooks --interval 60 --include-restarting
SSH_PORT=22
-include local_registry.mk
include common.mk
