# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM alpine/git as source

WORKDIR /
RUN git clone https://chromium.googlesource.com/chromiumos/platform/moblab

##############################################################################

FROM mariadb:10.2

COPY --from=source /moblab/src/service_settings/mysql_defaults_extra.cnf \
    /etc/mysql/conf.d/

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

RUN chown -R moblab:moblab /var/lib/mysql

USER moblab:moblab
