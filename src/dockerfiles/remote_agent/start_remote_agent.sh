#!/bin/bash
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
set -x

while [ ! -f /home/moblab/.service_account.json ]
do
  echo "The service account file does not exist, not starting the remote agent server!"
  sleep 2m
done

/etc/moblab/remote_agent/server.py -v
