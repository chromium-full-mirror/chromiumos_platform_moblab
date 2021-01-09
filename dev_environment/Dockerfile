# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM gcr.io/chromeos-partner-moblab/moblab-dev-environment:release

ARG USER
ARG USERID

WORKDIR /moblab_source

RUN chmod uog+rx /usr/local/bin/get_source.sh

RUN adduser --gecos "" --disabled-password --uid ${USERID} ${USER}

RUN echo "$USER     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ENV PATH=/moblab_source/depot_tools:$PATH

RUN chown -R $USER /moblab_source
RUN chmod u+rwx /moblab_source

ENV DISPLAY=:0
USER $USER

CMD ["entry.sh"]