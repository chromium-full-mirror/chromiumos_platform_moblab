# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

all: compile_proto


clean_proto:
	rm -f ${T}/src/app/services/moblabrpc*pb*

compile_proto: clean_proto
	protoc \
                -I="../moblab-rpcserver" \
		--js_out=import_style=commonjs:src/app/services \
                --grpc-web_out="import_style=commonjs+dts,mode=grpcwebtext:src/app/services" \
                "../moblab-rpcserver/moblabrpc.proto"
