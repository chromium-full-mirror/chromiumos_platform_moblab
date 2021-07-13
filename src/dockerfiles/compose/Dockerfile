# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers

FROM ${BASE_REGISTRY_URI}/docker/compose:alpine-1.27.4

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=autopush
ARG WATCHTOWER_CMD="--interval 3600 --monitor-only"
ARG SSH_PORT

# If the args left empty the script will leave the values in .env as is.
ARG BUILD_VERSION
ARG DB_VER
ARG DB_INIT_VER
ARG DB_SETUP_VER
ARG DEVSERVER_VER
ARG AUTOTEST_AFE_VER
ARG AT_DBSETUP_VER
ARG AT_MONITORDB_VER
ARG AT_HOSTSCHEDULER_VER
ARG AT_JOBABORTER_VER
ARG MOBLAB_UI_VER
ARG MOBLAB_RPCSERVER_VER
ARG REMOTE_AGENT_VER
ARG OFFLOADER_VER
ARG REMOTE_SCHEDULER_VER
ARG REMOTE_ACCESS_VER
ARG ENVOYPROXY_VER
ARG MOBMONITOR_VER
ARG DNS_VER
ARG LOGROTATE_VER
ARG DUT_MANAGER_VER
ARG DUT_MANAGER_STORAGE_VER


ENV LABEL="${LABEL}"
ENV REGISTRY_URI="${REGISTRY_URI}"
ENV WATCHTOWER_CMD="${WATCHTOWER_CMD}"
ENV SSH_PORT="${SSH_PORT}"

WORKDIR /
COPY docker-compose.yaml .
COPY docker-compose.watchtower.yaml .
COPY docker-compose.override.yml* .
COPY .env main.env
COPY override.env* .
COPY compose_startup.sh .
RUN chmod u+x compose_startup.sh

COPY override_service_version.sh .
RUN chmod u+x override_service_version.sh

RUN ./override_service_version.sh DB ${DB_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh DB_INIT ${DB_INIT_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh DB_SETUP ${DB_SETUP_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh DEVSERVER ${DEVSERVER_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh AUTOTEST_AFE ${AUTOTEST_AFE_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh AT_DBSETUP ${AT_DBSETUP_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh AT_MONITORDB ${AT_MONITORDB_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh AT_HOSTSCHEDULER ${AT_HOSTSCHEDULER_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh AT_JOBABORTER ${AT_JOBABORTER_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh MOBLAB_UI ${MOBLAB_UI_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh MOBLAB_RPCSERVER ${MOBLAB_RPCSERVER_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh REMOTE_AGENT ${REMOTE_AGENT_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh OFFLOADER ${OFFLOADER_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh REMOTE_SCHEDULER ${REMOTE_SCHEDULER_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh REMOTE_ACCESS ${REMOTE_ACCESS_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh ENVOYPROXY ${ENVOYPROXY_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh MOBMONITOR ${MOBMONITOR_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh DNS ${DNS_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh LOGROTATE ${LOGROTATE_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh DUT_MANAGER ${DUT_MANAGER_VER:-${BUILD_VERSION}}
RUN ./override_service_version.sh DUT_MANAGER_STORAGE ${DUT_MANAGER_STORAGE_VER:-${BUILD_VERSION}}


ENTRYPOINT ["/compose_startup.sh"]

# Test the config for syntax errors
RUN docker-compose config
