# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

#############
### build ###
#############

# base image
FROM python:3.8-buster as build

RUN apt-get update && apt-get install -yq unzip cmake wget

COPY src/dockerfiles/offloader/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /
RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v3.10.0/protoc-3.10.0-linux-x86_64.zip
RUN unzip protoc-3.10.0-linux-x86_64.zip
RUN cp bin/protoc /usr/local/bin
COPY third_party/autotest/tko/tko.proto /usr/local/autotest/tko/tko.proto
RUN protoc --proto_path /usr/local/autotest/tko --python_out=/usr/local/autotest/tko /usr/local/autotest/tko/tko.proto

# moblab_common
WORKDIR /moblab_common
COPY src/moblab_common/ .
RUN cp setup.py /
RUN python /setup.py install

WORKDIR /etc/moblab/moblab_results_uploader
COPY src/moblab_results_uploader/ /etc/moblab/moblab_results_uploader

############
### prod ###
############

# base image
FROM python:3-slim-buster

# copy artifact build from the 'build environment'
COPY --chown=moblab --from=build /usr/local/autotest /usr/local/autotest
COPY --chown=moblab --from=build /etc/moblab/moblab_results_uploader /etc/moblab/moblab_results_uploader
COPY --from=build /usr/local/lib/python3.8/site-packages \
    /usr/local/lib/python3.8/site-packages

# run moblab_results_uploader

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab
RUN apt-get update && apt-get install -yq sudo
RUN echo "moblab     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN usermod -aG sudo moblab

RUN mkdir -p /var/log/moblab/offloader
RUN chown -R moblab /var/log/moblab

RUN chown -R moblab /etc/moblab/moblab_results_uploader
RUN chmod u+x /etc/moblab/moblab_results_uploader/moblab_results_uploader
USER moblab

ENTRYPOINT ["/etc/moblab/moblab_results_uploader/moblab_results_uploader"]
