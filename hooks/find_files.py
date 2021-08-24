#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""In the current git commit and find the py files in that commit."""

import os
import sys
from git import Repo
import argparse

BASE_DIR = os.environ["PWD"]
IGNORE_DIR_LIST = ["third_party/"]


def find_files(file_extensions):
    """Find files in a regular commit that end with the given extension.

    Args:
        file_extensions (list): list of file extension strings.
    """
    repo = Repo("/moblab_source/moblab")
    commit = repo.commit("HEAD")
    if len(commit.parents) > 1:
        sys.exit(0)

    diffs = repo.index.diff("HEAD")

    filenames = []
    for diff in diffs:
        filename = "%s/%s" % (BASE_DIR, diff.b_path)
        ignored = len(
            [
                ignore_dir
                for ignore_dir in IGNORE_DIR_LIST
                if ignore_dir in filename
            ]
        )
        correct_extension = (
            len(
                [
                    extension
                    for extension in file_extensions
                    if filename.endswith(extension)
                ]
            )
            != 0
        )
        if not ignored and correct_extension and os.path.exists(filename):
            filenames.append(filename)
    print(" ".join(filenames))


def main(argv):
    """Script entry point that provides arg parser and wrapper to find files.

    Args:
        argv (list): list of provided command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-e",
        "--extensions",
        nargs="*",
        type=str,
        required=True,
        help="File extensions to find.",
    )
    parser.add_argument(
        "-i",
        "--ignore_dirs",
        nargs="*",
        type=str,
        required=False,
        help="Ignore the given directories.",
    )

    options = parser.parse_args(argv)
    if options.ignore_dirs:
        IGNORE_DIR_LIST.extend(options.ignore_dirs)

    find_files(options.extensions)


if __name__ == "__main__":
    main(sys.argv[1:])
