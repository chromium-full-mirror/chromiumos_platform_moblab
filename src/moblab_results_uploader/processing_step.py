# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""This module defines some common utils for processing the test results."""

from __future__ import print_function


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


class DataProcessFlow(object):
    """A data process flow.

    The instance of this class calls all registered data process components one
    by one. The processing result of each component is passed to the next
    component as the input.
    """

    def __init__(self, *steps):
        self._steps = steps

    async def __call__(self, data):
        for step in self._steps:
            data = await step(data)

        return data
