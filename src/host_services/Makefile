# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

PROTO = "hostservices.proto"
WORKDIR="/tmp"
PROTO_OUT_DIR = ${WORKDIR}/host_services

all:
	mkdir -p ${PROTO_OUT_DIR}
	rm ${WORKDIR}/host_services/*pb2*
	python -m grpc_tools.protoc \
		-I="." \
		--python_out=":${PROTO_OUT_DIR}" \
		--grpc_python_out=":${PROTO_OUT_DIR}" \
	        ${PROTO}

install:
	install -t ${DESTDIR}etc/moblab/host_services -D ${PROTO_OUT_DIR}/*
	install -D *.py ${DESTDIR}etc/moblab/host_services
