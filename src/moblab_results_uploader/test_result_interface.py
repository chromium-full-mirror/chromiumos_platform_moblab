# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import print_function

import abc
import pathlib


class TestResultError(Exception):
    """Exception for TestResult class."""


class TestResult(abc.ABC):
    """The interface class for all TestResult classes."""
    GLOB_PATTERN = '*'

    def __init__(self, *, description, root_dir, relative_path):
        """Constrcutor of the class.

        Args:
            description: A description of the test result directory, e.g.
                AutotestJob, Swarming task, etc.
            root_dir: A pathlib.Path object or a string of the root directory
                of the test result.
            relative_path: A pathlib.Path object or a string of the test result
                path relative to the `root_dir`. Cannot start with './'.
            """
        self._description = description
        self._relative_path = pathlib.Path(relative_path)
        self._abs_path = pathlib.Path(root_dir) / relative_path

    def __str__(self):
        return '<{}: {}>'.format(self._description, self.name)

    @property
    def name(self):
        return str(self._relative_path)

    @property
    def abs_path(self):
        return self._abs_path

    @property
    @abc.abstractmethod
    def id(self):
        """Return the ID of the test result.

        Returns:
            The string of test result ID.
        """
        raise NotImplementedError('TestResult.id')

    @property
    @abc.abstractmethod
    def finished_time(self):
        """Return the finished time of the test result.

        Returns:
            The datetime.datetime object of finished time, or None if the test
            is not finished yet.
        """
        raise NotImplementedError('TestResult.finished_time')

    @property
    @abc.abstractmethod
    def succeeded(self):
        """Return if the test succeeded.

        Returns:
            True when the test finished successfully, or False when finished
            with problems, or None when not finished yet.
        """
        raise NotImplementedError('TestResult.succeeded')
