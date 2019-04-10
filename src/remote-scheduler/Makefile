# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

PROTO_OUT_DIR = ${WORKDIR}/remote-scheduler

all:
	mkdir -p ${PROTO_OUT_DIR}
	protoc \
		-I="." \
		--python_out=":${PROTO_OUT_DIR}" \
		"moblab_request.proto" || die

install:
	install -t ${DESTDIR}etc/moblab/remote-scheduler -D ${PROTO_OUT_DIR}/*
	ls *.py | grep -v _unittest | \
		xargs -i install -t ${DESTDIR}etc/moblab/remote-scheduler {}

