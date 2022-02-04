# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

ARG BASE_REGISTRY_URI=us-docker.pkg.dev/chromeos-partner-moblab/base-containers
ARG REGISTRY_URI=gcr.io/chromeos-partner-moblab
ARG LABEL=autopush
######################################################################

FROM ${BASE_REGISTRY_URI}/node:16 as build

# install chrome for protractor tests
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
# RUN apt-get update && apt-get install -yq google-chrome-stable

RUN npm install -g gts eslint
ENV NODE_PATH=/usr/local/lib/node_modules/gts/node_modules:/usr/local/lib/node_modules

WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH


# install and cache app dependencies
# add app
COPY ./moblab-ui/package.json /app
COPY ./moblab-ui/package-lock.json /app

RUN npm install --ignore-scripts

RUN ngcc

# install and cache app dependencies
# add app
COPY ./moblab-ui /app

# run tests
#RUN ng test --watch=false
#RUN ng e2e --port 4202

RUN ng build --output-path=dist --output-hashing=all --configuration=production

######################################################################

# base image
FROM ${BASE_REGISTRY_URI}/nginx:alpine

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
     --disabled-password --gecos "" moblab

RUN mkdir -p /var/cache/nginx/client_temp
RUN mkdir -p /var/cache/nginx/proxy_temp
RUN chown -R moblab /var/cache/nginx
RUN chmod -R uog+rw /var/run

# copy artifact build from the 'build environment'
COPY --chown=moblab --from=build /app/dist /etc/nginx/html/

COPY --chown=moblab moblab-ui/nginx.conf /etc/nginx
RUN rm -f /etc/nginx/conf.d/*
RUN rm -f /docker-entrypoint.d/*
RUN rm -f /var/log/nginx/*
RUN chmod uog+rw /var/log/nginx
RUN chown -R moblab:moblab /var/log/nginx


EXPOSE 6010

USER moblab

# run nginx
CMD ["nginx", "-g", "daemon off;"]
