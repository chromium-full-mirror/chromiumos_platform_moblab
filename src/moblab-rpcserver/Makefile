# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

PROTOS = "moblabrpc.proto"

PROTO_OUT_DIR = ${WORKDIR}/moblab-rpcserver

all:
	mkdir -p ${PROTO_OUT_DIR}
	protoc \
		-I="." \
		--python_out=":${PROTO_OUT_DIR}" \
		--grpc_python_out=":${PROTO_OUT_DIR}" \
		--plugin=protoc-gen-grpc_python=/usr/bin/grpc_python_plugin \
		"moblabrpc.proto" || die

install:
	install -t ${DESTDIR}etc/moblab/moblab-rpcserver -D ${PROTO_OUT_DIR}/*
	ls *.py | grep -v _unittest | grep -v _pb2.py | \
		xargs -i install -t ${DESTDIR}etc/moblab/moblab-rpcserver {}
