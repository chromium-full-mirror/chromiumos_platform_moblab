#!/bin/sh
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

if [ -f "/var/log/dns.log" ]; then
    chown moblab:moblab /var/log/dns.log
fi
/usr/sbin/dnsmasq --no-daemon --user=moblab --group=moblab