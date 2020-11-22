#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""In the current git commit and find the py files in that commit."""

import os
import sys
from git import Repo

BASE_DIR = os.environ["PWD"]


def find_python_files():
    """Ensure that the .env file being checked in only contains =autopush."""
    repo = Repo("/moblab_source/moblab")
    commit = repo.commit("HEAD")
    if len(commit.parents) > 1:
        sys.exit(0)

    diffs = repo.index.diff("HEAD")

    filenames = []
    for diff in diffs:
        filename = "%s/%s" % (BASE_DIR, diff.b_path)
        if (
            filename.endswith(".py")
            and "third_party/" not in filename
            and os.path.exists(filename)
        ):
            filenames.append(filename)
    print(" ".join(filenames))


def main(unused_argv):
    """Find files in a regular commit that end in py.

    Args:
        unused_argv (list): currently unused.
    """
    find_python_files()


if __name__ == "__main__":
    main(sys.argv[1:])
