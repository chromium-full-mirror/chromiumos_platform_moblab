# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# TODO(gregorynisbet): Remove quotes from make variables.
PROTO := "hostservice.proto"
WORKDIR := "/tmp"
PROTO_OUT_DIR := ${WORKDIR}/host_service

PKG_CONFIG ?= pkg-config
PKG_DEPS = libusb-1.0
PKG_LIBS := $(shell $(PKG_CONFIG) --libs $(PKG_DEPS))
PKG_CFLAGS := $(shell $(PKG_CONFIG) --cflags $(PKG_DEPS))

.PHONY: all

all: reset_usb proto

reset_usb:
	$(CC) $(CFLAGS) $(CPPFLAGS) $(PKG_CFLAGS) -c r_usb.c -o $(TMPDIR)/r_usb.o
	$(CC) $(CFLAGS) $(LFLAGS) $(TMPDIR)/r_usb.o $(PKG_LIBS) -o $(TMPDIR)/reset_usb


proto:
	mkdir -p ${PROTO_OUT_DIR}
	rm -f ${WORKDIR}/host_service/*pb2*
	python -m grpc_tools.protoc \
		-I="../common" \
		--python_out=":${PROTO_OUT_DIR}" \
		--grpc_python_out=":${PROTO_OUT_DIR}" \
	        ${PROTO}

install:
	@mkdir -p $(DESTDIR)usr/bin
	install $(TMPDIR)/reset_usb ${DESTDIR}usr/bin
	install -t ${DESTDIR}etc/moblab/host_server -D ${PROTO_OUT_DIR}/*
	install -D host_server_chromeos.py ${DESTDIR}etc/moblab/host_server
	install -D ../common/host*.py ${DESTDIR}etc/moblab/host_server
	@mkdir -p ${DESTDIR}etc/moblab/host_server/utils
	install -D ../common/utils/*.py ${DESTDIR}etc/moblab/host_server/utils
