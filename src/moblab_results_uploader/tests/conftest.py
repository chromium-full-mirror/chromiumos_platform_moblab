# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""The configuration python file for Pytest.

In this file, we add below customized command line options:
    --network: Run tests depend on network connectivity to Google Storage.
    --gs-bucket: (string) The name of a GS bucket for testing.
    --credentials-file: (string) The path of credentials file to access the
                        bucket.
"""

from __future__ import print_function

import asynctest

import pytest


def pytest_addoption(parser):
    parser.addoption('--network', action='store_true', default=False,
                     help='Run tests that depend on good network connectivity')
    parser.addoption(
        '--gs-bucket', help='The GS bucket name for testing.'
    )
    parser.addoption(
        '--credentials-file', help='The valid credentials file to access GS.'
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption('--network'):
        # run network tests
        return

    skip_network_tests = pytest.mark.skip(
        reason='Skipping network test (re-run w/--network)')

    for item in items:
        if 'network' in item.keywords:
            item.add_marker(skip_network_tests)


@pytest.fixture
def next_step():
    return asynctest.mock.CoroutineMock()


@pytest.fixture
def gs_bucket(request):
    return request.config.getoption('--gs-bucket')


@pytest.fixture
def credentials_file(request):
    return request.config.getoption('--credentials-file')
