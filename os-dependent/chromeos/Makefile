# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

PROTO = "hostservice.proto"
WORKDIR="/tmp"
PROTO_OUT_DIR = ${WORKDIR}/host_service

all:
	mkdir -p ${PROTO_OUT_DIR}
	rm -f ${WORKDIR}/host_service/*pb2*
	python -m grpc_tools.protoc \
		-I="../common" \
		--python_out=":${PROTO_OUT_DIR}" \
		--grpc_python_out=":${PROTO_OUT_DIR}" \
	        ${PROTO}

install:
	install -t ${DESTDIR}etc/moblab/host_server -D ${PROTO_OUT_DIR}/*
	install -D host_server_chromeos.py ${DESTDIR}etc/moblab/host_server
	install -D ../common/host*.py ${DESTDIR}etc/moblab/host_server
