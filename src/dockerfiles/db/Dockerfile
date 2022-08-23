# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
FROM ${BASE_REGISTRY_URI}/mariadb:10.5

ARG UID=246

COPY mysql_defaults_extra.cnf /etc/mysql/conf.d/

# Tools that are useful for debugging/ tuning settings on the database, here
# for documentation, not for production use.
# RUN apt-get update && apt-get install --no-install-recommends -yq \
#     git wget

# WORKDIR /tmp
# ENV GIT_SSL_NO_VERIFY=true
# RUN git clone https://github.com/FromDual/mariadb-sys.git
# RUN wget --no-check-certificate https://raw.githubusercontent.com/major/MySQLTuner-perl/master/mysqltuner.pl
# WORKDIR /

RUN addgroup --gid $UID moblab && adduser --ingroup moblab --uid $UID \
    --disabled-password --gecos "" moblab

RUN chown -R moblab:moblab /var/lib/mysql

USER moblab:moblab
