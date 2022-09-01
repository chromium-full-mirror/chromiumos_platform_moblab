# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import setuptools

setuptools.setup(
    name="moblab_common",
    version="0.2",
    packages=setuptools.find_packages("/src"),
    package_dir={"": "/src"},
    install_requires=[
        "future",
        "requests",
        "google-cloud-storage",
        "google-cloud-pubsub",
        "docker",
        "parallel-ssh",
        "python-nmap",
        "protobuf==3.17.0",
        "sqlalchemy",
        "pymysql",
    ],
    scripts=[
        "/src/tools/create-moblab-id.py",
    ],
)
