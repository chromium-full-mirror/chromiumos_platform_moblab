# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

PROTO = hostservice.proto
INSTALL_DIR = /etc/moblab/host_server

.PHONY: all init clean

all: init dependencies host_server

developer: init dependencies host_server local_registry

dependencies:
	apt install pip
	pip install -y grpcio-tools netifaces

local_registry:
	service docker stop
	# Remove the first line - should be open bracket.
	# TODO fix this so if the file is empty it works correctly.
	sed -i '1d' /etc/docker/daemon.json
	# Add in our insecure registry 
	REGIPADDR=$(hostname -I | awk -F ' ' '{print $1}') \
	sed -i "1 i\{\n  \"insecure-registries\": [\"${REGIPADDR}:5000\"]," /etc/docker/daemon.json
	cat /etc/docker/daemon.json
	service docker start
	cp init/moblab-docker-registry /etc/init.d
	systemctl daemon-reload
	systemctl enable moblab-docker-registry.service
	systemctl start moblab-docker-registry.service

init:
	mkdir -p ${INSTALL_DIR}
	mkdir -p /var/log/bootup/
	chmod uog+rw /var/log/bootup

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

host_server: python
		cp init/ moblab-host-server /etc/init.d;
		systemctl daemon-reload;
		systemctl enable moblab-host-server.service;
		systemctl start moblab-host-server.service;
	done

networking:
	cp init/moblab-networking /etc/init.d
	systemctl daemon-reload
	systemctl enable moblab-networking.service
	systemctl start moblab-networking.service



