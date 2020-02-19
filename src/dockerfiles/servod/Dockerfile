# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FROM debian:buster

RUN apt update

RUN apt install -y wget python-pexpect python-numpy python-setuptools python-serial python-pytest tidy libftdi-dev curl gcc make pkg-config libudev-dev usbutils

RUN wget https://github.com/libusb/libusb/releases/download/v1.0.23/libusb-1.0.23.tar.bz2
RUN tar xvf libusb-1.0.23.tar.bz2
WORKDIR /libusb-1.0.23

RUN ./configure && make && make install
RUN export LD_LIBRARY_PATH=/usr/local/lib


WORKDIR /
RUN wget https://chromium.googlesource.com/chromiumos/platform/standalone-hdctools/+archive/master.tar.gz
RUN tar xvf master.tar.gz

COPY servod/start_servod.sh ./

RUN ./servod install
