# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

all: compile_node

copy_modules:
	if [ ! -d "${T}/node_modules" ]; then \
		cp -r "${WORKDIR}/moblab-ui/node_modules" ${T};\
	fi

copy_src: copy_modules
	cp -r * ${T}

compile_proto: copy_src
	protoc \
                -I="${S}/src/moblab-rpcserver" \
		--js_out=import_style=commonjs:${T}/src/app/services \
                --grpc-web_out="import_style=commonjs+dts,mode=grpcwebtext:${T}/src/app/services" \
                "${S}/src/moblab-rpcserver/moblabrpc.proto" || die

compile_node: compile_proto
	cd ${T}; node ./node_modules/.bin/ng build \
		--prod \
		--output-path=${WORKDIR}/dist || die;

install:
	install -d ${DESTDIR}etc/moblab/moblab-ui/static
	install -d ${DESTDIR}etc/moblab/moblab-ui/static/assets
	install moblab-ui.py ${DESTDIR}etc/moblab/moblab-ui/moblab-ui.py
	cp -r ${WORKDIR}/dist/* ${DESTDIR}etc/moblab/moblab-ui/static
