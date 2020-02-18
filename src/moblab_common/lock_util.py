# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Locking related utility functions."""

import contextlib
import errno
import fcntl
import os
import time


@contextlib.contextmanager
def file_lock(lock_file_path, exclusive=False, timeout_seconds=None):
    """A simple file lock to sync multiple processes.

    Args:
        lock_file_path: The path of lock file. Must be writable.
        exclusive: True indicates lock for writing. Otherwise, for reading.
        timeout_seconds: Timeout for the locking. None indicates no timeout.
    """
    fd = os.open(lock_file_path, os.O_CREAT)
    start_time = time.time()
    lock_cmd = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
    while True:
        try:
            fcntl.flock(fd, lock_cmd | fcntl.LOCK_NB)
            break
        except (IOError, OSError) as err:
            if err.errno != errno.EAGAIN:
                raise
            if timeout_seconds is not None and \
                    time.time() - start_time > timeout_seconds:
                raise
            time.sleep(0.1)

    yield
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
    try:
        os.unlink(lock_file_path)
    except Exception:
        pass
