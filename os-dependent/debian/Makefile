# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

PROTO = hostservice.proto
INSTALL_DIR = /etc/moblab/host_server

.PHONY: all init clean

all: init install

init:
	mkdir -p ${INSTALL_DIR}

clean:
	rm -rf ${INSTALL_DIR}

proto: init
	mkdir -p /tmp/proto_bin
	docker run -u root -t -v /tmp/proto_bin:/tmp \
		gcr.io/chromeos-partner-moblab/protoc:release cp -R /protoc /tmp
	PATH=/tmp/proto_bin/protoc:${PATH}
	rm -f /etc/moblab/host_server/*pb2*
	python3 -m grpc_tools.protoc \
		-I="../common" \
		--python_out=":${INSTALL_DIR}" \
		--grpc_python_out=":${INSTALL_DIR}" \
	        ${PROTO}
	rm -rf /tmp/proto_bin

python: proto
	install -D host_server_debian.py ${INSTALL_DIR}
	install -D ../common/host*.py ${INSTALL_DIR}

INIT_FILES := moblab-docker-registry moblab-host-server
install: python
	for file in $(INIT_FILES); do \
		cp init/$${file} /etc/init.d; \
		systemctl daemon-reload; \
		systemctl enable $${file}.service; \
		systemctl start $${file}.service; \
	done

networking:
	cp init/moblab-networking /etc/init.d
	systemctl daemon-reload
	systemctl enable moblab-networking.service
	systemctl start moblab-networking.service



