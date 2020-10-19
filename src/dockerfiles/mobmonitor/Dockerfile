# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=release

###############################################################################
FROM node:12 as build

# install chrome for protractor tests
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
# RUN apt-get update && apt-get install -yq google-chrome-stable

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install and cache app dependencies
# doing the package files first allows for faster compiles when developing
# as docker will cache the npm packages
RUN mkdir -p /app
COPY src/mobmonitor-ui/package.json /app
COPY src/mobmonitor-ui/package-lock.json /app
RUN npm install

# run tests
#RUN ng test --watch=false
#RUN ng e2e --port 4202

# generate build
COPY src/mobmonitor-ui /app
RUN ng build --output-path=dist --output-hashing=all --configuration=production

#########################################################################################3

FROM ${REGISTRY_URI}/moblab_common:${LABEL} as common

#########################################################################################3

FROM python:3.8-slim-buster

WORKDIR /

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 --disabled-password --gecos "" moblab
RUN apt-get update && apt-get install -yq gcc iputils-ping usbutils procps

RUN apt-get update && apt-get install -yq \
    libssl-dev \
    zlib1g-dev \
    gcc-multilib \
    cmake \
    curl

COPY src/dockerfiles/mobmonitor/requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /wheels
COPY --from=common /wheel/*py3* .
RUN pip install *.whl
RUN rm -rf /wheels

WORKDIR /etc/moblab/mobmonitor
COPY --chown=moblab src/mobmonitor/ /etc/moblab/mobmonitor
# copy artifact build from the 'build environment'
RUN mkdir -p /etc/moblab/mobmonitor/static/
COPY --chown=moblab --from=build /app/dist /etc/moblab/mobmonitor/static/

RUN mkdir -p /var/log/mobmonitor/
RUN chown -R moblab /var/log/mobmonitor

RUN addgroup --gid 412 docker
RUN usermod -aG docker moblab

RUN apt purge -yq cmake zlib1g-dev gcc-multilib
RUN apt autoremove -yq
RUN apt-get clean

USER moblab

ENTRYPOINT ["/usr/local/bin/python", "/etc/moblab/mobmonitor/mobmonitor.py"]
