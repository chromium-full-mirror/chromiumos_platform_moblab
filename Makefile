# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
SUBDIRS := remote-scheduler
INSTALL_SUBDIRS = $(SUBDIRS)
all:
	for dir in $(SUBDIRS); do \
                $(MAKE) -C src/$$dir || exit 1; \
        done
install:
	for dir in $(SUBDIRS); do \
                $(MAKE) -C src/$$dir install; \
        done
