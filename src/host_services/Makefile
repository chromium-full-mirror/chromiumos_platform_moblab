# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

PROTO = "hostservices.proto"
WORKDIR="/tmp"
PROTO_OUT_DIR = ${WORKDIR}/host-services

all:
	mkdir -p ${PROTO_OUT_DIR}
	python -m grpc_tools.protoc \
		-I="." \
		--python_out=":${PROTO_OUT_DIR}" \
		--grpc_python_out=":${PROTO_OUT_DIR}" \
	        ${PROTO}

install:
	install -t ${DESTDIR}etc/moblab/host-services -D ${PROTO_OUT_DIR}/*
	install -D *.py ${DESTDIR}etc/moblab/host-services
