# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM alpine/git as source

WORKDIR /
RUN git clone https://chromium.googlesource.com/chromiumos/chromite

WORKDIR /devserver-src
RUN git clone https://chromium.googlesource.com/chromiumos/platform/dev-util
RUN ls /devserver-src/dev-util
RUN sed -i 's#python2#python3#g' /devserver-src/dev-util/devserver.py
######################################################################

FROM debian:buster as run

COPY --from=source /devserver-src /devserver-src
COPY --from=source /chromite /chromite

# Install packages
RUN apt-get update && apt-get install --no-install-recommends -yq \
    curl python3 sudo gcc python-dev procps \
    bzip2 unzip sudo ca-certificates python3-distutils python3-dev

RUN update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2

COPY requirements.txt ./

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt
ENV DESTDIR="/"

WORKDIR /
COPY setup_chromite.py /
RUN python -m pip install setuptools
RUN python /setup_chromite.py install

# Devserver requires an apache server to be running for a good health check
# this is a fake apache script that just sleeps forever.
# TODO remove requirement from devserver to need an apache process.
COPY apache2 /bin

WORKDIR /devserver-src/dev-util

RUN install -m 0755 host/start_devserver "/usr/bin"

RUN mkdir /usr/lib/devserver
RUN install -m 0755 devserver.py strip_package.py /usr/lib/devserver
RUN install -m 0644  \
        autoupdate.py \
        builder.py \
        cherrypy_ext.py \
        health_checker.py \
        nebraska/nebraska.py \
        setup_chromite.py \
        /usr/lib/devserver

RUN mkdir /static

EXPOSE 8080

## Add moblab user
RUN addgroup --gid 246 moblab && \
    adduser --gecos "" --ingroup moblab \
       --disabled-password --uid 246 moblab
RUN echo "moblab     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN mkdir -p /static/cache
RUN chown -R moblab:moblab /static
RUN mkdir -p /var/log/moblab/devserver/
RUN chown -R moblab:moblab /var/log/moblab

RUN apt-get install --reinstall sudo

USER moblab

CMD ["/usr/lib/devserver/devserver.py", "--production", \
     "--static_dir=/static", "--logfile", \
     "/var/log/moblab/devserver/server.log", \
     "/var/log/moblab/devserver/console.log"]


