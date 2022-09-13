#!/bin/bash
# Copyright 2022 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

if [ `whoami` != root ]; then
    echo Please run this script as root or using sudo
    exit
fi

make all

echo "Installing script that control moblab application."
install moblab_start.sh /usr/local/bin
install moblab_stop.sh /usr/local/bin
install moblab_reset.sh /usr/local/bin
install moblab_setup_configuration.conf /usr/local/bin

# setup the network
make networking
