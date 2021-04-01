# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers

FROM ${BASE_REGISTRY_URI}/docker/compose:alpine-1.27.4

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=autopush
ARG WATCHTOWER_CMD="--interval 3600 --monitor-only"
ARG SSH_PORT

# By convention if specific version is not set use ... hm
ARG BUILD_VERSION
ARG DB_VER=${BUILD_VERSION}
ARG DB_INIT_VER=${BUILD_VERSION}
ARG DB_SETUP_VER=${BUILD_VERSION}
ARG DEVSERVER_VER=${BUILD_VERSION}
ARG AUTOTEST_AFE_VER=${BUILD_VERSION}
ARG AT_DBSETUP_VER=${BUILD_VERSION}
ARG AT_MONITORDB_VER=${BUILD_VERSION}
ARG AT_HOSTSCHEDULER_VER=${BUILD_VERSION}
ARG AT_JOBABORTER_VER=${BUILD_VERSION}
ARG MOBLAB_UI_VER=${BUILD_VERSION}
ARG MOBLAB_RPCSERVER_VER=${BUILD_VERSION}
ARG REMOTE_AGENT_VER=${BUILD_VERSION}
ARG OFFLOADER_VER=${BUILD_VERSION}
ARG REMOTE_SCHEDULER_VER=${BUILD_VERSION}
ARG REMOTE_ACCESS_VER=${BUILD_VERSION}
ARG ENVOYPROXY_VER=${BUILD_VERSION}
ARG WATCHTOWER_VER=${BUILD_VERSION}
ARG MOBMONITOR_VER=${BUILD_VERSION}
ARG DNS_VER=${BUILD_VERSION}
ARG LOGROTATE_VER=${BUILD_VERSION}


ENV LABEL="${LABEL}"
ENV REGISTRY_URI="${REGISTRY_URI}"
ENV WATCHTOWER_CMD="${WATCHTOWER_CMD}"
ENV SSH_PORT="${SSH_PORT}"

WORKDIR /
COPY docker-compose.yaml .
COPY docker-compose.override.yml* .
COPY .env main.env
COPY override.env* .
COPY compose_startup.sh .
RUN chmod u+x compose_startup.sh

COPY override_service_version.sh .
RUN chmod u+x override_service_version.sh

RUN ./override_service_version.sh DB ${DB_VER}
RUN ./override_service_version.sh DB_INIT ${DB_INIT_VER}
RUN ./override_service_version.sh DB_SETUP ${DB_SETUP_VER}
RUN ./override_service_version.sh DEVSERVER ${DEVSERVER_VER}
RUN ./override_service_version.sh AUTOTEST_AFE ${AUTOTEST_AFE_VER}
RUN ./override_service_version.sh AT_DBSETUP ${AT_DBSETUP_VER}
RUN ./override_service_version.sh AT_MONITORDB ${AT_MONITORDB_VER}
RUN ./override_service_version.sh AT_HOSTSCHEDULER ${AT_HOSTSCHEDULER_VER}
RUN ./override_service_version.sh AT_JOBABORTER ${AT_JOBABORTER_VER}
RUN ./override_service_version.sh MOBLAB_UI ${MOBLAB_UI_VER}
RUN ./override_service_version.sh MOBLAB_RPCSERVER ${MOBLAB_RPCSERVER_VER}
RUN ./override_service_version.sh REMOTE_AGENT ${REMOTE_AGENT_VER}
RUN ./override_service_version.sh OFFLOADER ${OFFLOADER_VER}
RUN ./override_service_version.sh REMOTE_SCHEDULER ${REMOTE_SCHEDULER_VER}
RUN ./override_service_version.sh REMOTE_ACCESS ${REMOTE_ACCESS_VER}
RUN ./override_service_version.sh ENVOYPROXY ${ENVOYPROXY_VER}
RUN ./override_service_version.sh WATCHTOWER ${WATCHTOWER_VER}
RUN ./override_service_version.sh MOBMONITOR ${MOBMONITOR_VER}
RUN ./override_service_version.sh DNS ${DNS_VER}
RUN ./override_service_version.sh LOGROTATE ${LOGROTATE_VER}


ENTRYPOINT ["/compose_startup.sh"]

# Test the config for syntax errors
RUN docker-compose config
