# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""This module defines some common utils for processing the test results."""




class ProcessStep(object):
    """A base class for define a processing step.

    It's not required we must derive a new processing step from this class.
    It's only recommended when we required to change the `next_step` after we
    creating the processing step coroutine.
    But in generally, inheriting from this class can bring better readability.
    """

    def __init__(self, *, next_step=None):
        """Constructor.

        Args:
            next_step: The next coroutine in the whole processing pipeline."""
        self._next_step = next_step

    def next_step(self, new_step):
        """A setter for property `next_step`."""
        self._next_step = new_step

    next_step = property(None, next_step)
