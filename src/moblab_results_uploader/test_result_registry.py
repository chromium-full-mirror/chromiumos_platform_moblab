# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A data structure for all test result classes registering."""


import collections
import autotest_result


REGISTRY = []


class TestResultRegisteryEntry(collections.namedtuple(
        'TestResultRegisteryEntry', ['root_dir', 'classes'])):
    """TestResultRegisteryEntry is used to register test results.

    Args:
        root_dir: An object of pathlib.Path to represent the root directory of
            tests results. Take Autotest as an example, the root directory can
            be pathlib.Path('/usr/local/autotest/results').
        classes: A list of classes which to create objects based on directories.
    """


REGISTRY.append(
    # Register for Autotest.
    TestResultRegisteryEntry(
        root_dir=autotest_result.ROOT_DIR,
        classes=[
            autotest_result.AutotestTestJob,
            autotest_result.AutotestHostTask
        ]
    )
)
