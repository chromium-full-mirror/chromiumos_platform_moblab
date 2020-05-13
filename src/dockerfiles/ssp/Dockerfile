# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM alpine/git as source

WORKDIR /

RUN git clone https://chromium.googlesource.com/chromiumos/chromite

###############################################################################

FROM debian:buster-slim as run

WORKDIR /

RUN addgroup --gid 246 moblab && adduser --ingroup moblab --uid 246 \
    --disabled-password --gecos "" moblab

COPY --from=source --chown=moblab /chromite /chromite

RUN apt-get update && apt-get install --no-install-recommends -yq \
        bzip2 \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        python \
        rsync \
        ssh \
        sudo \
        unzip \
        wget \
        iputils-ping

# Install the google cloud sdk
RUN echo \
    "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
    http://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg  \
    add - && apt-get update -y && apt-get install google-cloud-sdk -y

# Install the official pip
RUN wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
RUN python2.7 /tmp/get-pip.py --target /usr/lib/python2.7/dist-packages
COPY requirements.txt .
RUN python2.7 -m pip install --upgrade --no-cache-dir -r requirements.txt \
    --target /usr/local/lib/python2.7/dist-packages

# Java - required for CTS/GTS
# TODO - see if we can figure out two versions of the SSP and just load the
# java one for CTS.
RUN  wget https://download.java.net/java/GA/jdk9/9.0.4/binaries/\
openjdk-9.0.4_linux-x64_bin.tar.gz
RUN  tar xvf openjdk-9.0.4_linux-x64_bin.tar.gz
RUN  update-alternatives --install /usr/bin/java java \
    /jdk-9.0.4/bin/java 200000
RUN  update-alternatives --config java
# Java 9 has a issue where the ca certificates are not correct,
# get them from v 13
RUN  wget https://download.java.net/java/GA/jdk13.0.1/\
cec27d702aa74d5a8630c65ae61e4305/9/GPL/openjdk-13.0.1_linux-x64_bin.tar.gz
RUN  tar xvf openjdk-13.0.1_linux-x64_bin.tar.gz
RUN  cp jdk-13.0.1/lib/security/cacerts jdk-9.0.4/lib/security/
RUN  rm -rf jdk-13.0.1
RUN  rm -rf *.gz
RUN echo "moblab     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /usr/local/tast
RUN chown moblab:moblab /usr/local/tast
RUN mkdir -p /tmp/autotest-tradefed-cache
RUN chown moblab:moblab /tmp/autotest-tradefed-cache

USER moblab

ENV container=ssp_container
ENV AUTOTEST_WEB=autotest:8888

# Unlike lxc containers which you can start and will keep running on their own,
# docker containers require a running process or they exist.
# For SSP containers - we start them, execute commands then kill the container
# to mimic the lxc behaviour an artifical sleep is requried to keep the docker
# container running between commands.
CMD ["sleep", "infinity"]
