#!/bin/bash
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Distributed under the terms of the GNU General Public License v2.

node e2e/mock-backend-server.js &
ng e2e --proxy-config e2e/proxy-e2e.conf.json
pkill node
