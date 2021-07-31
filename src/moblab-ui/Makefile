# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

all: compile_proto install start


clean_proto:
	rm -f ./src/app/services/*_pb*

compile_proto: clean_proto
	./run_protogen_ui.sh

# TODO - fix the npm install errors that make the || true required.
install:
	npm install || true

start:
	npm start
