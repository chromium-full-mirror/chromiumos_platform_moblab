#!/usr/bin/python
#
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Tool for generating a moblab id"""
#TODO(haddokw)  refactor the code and break the dependency on autotest.
import common

from autotest_lib.client.common_lib import utils

if __name__ == '__main__':
    utils.get_moblab_id()
