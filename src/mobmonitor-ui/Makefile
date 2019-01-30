# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

APP_BASE="${DESTDIR}/etc/moblab/mobmonitor/static"

all:
	cp -r "${S}/src/mobmonitor-ui" "${WORKDIR}/src"
	mv "${WORKDIR}/node_modules" "${WORKDIR}/src/node_modules"
	cd "${WORKDIR}/src"; node ./node_modules/.bin/ng build --prod \
                        --extract-licenses=false --aot=false || die

install:
	install -t "${APP_BASE}" -D "${WORKDIR}"/src/dist/*
