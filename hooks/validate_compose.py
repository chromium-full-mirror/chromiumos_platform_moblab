#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""In the current git commit ensure env files are set to autopush."""

import sys
from git import Repo


def check_env_is_autopush():
    """Ensure that the .env file being checked in only contains =autopush."""
    repo = Repo("/moblab_source/moblab")
    commit = repo.commit("HEAD")
    if len(commit.parents) > 1:
        print("Not a regular commit")
        sys.exit(0)

    diffs = repo.index.diff("HEAD")

    for diff in diffs:
        filename = diff.b_path
        error = ""
        if filename.endswith(".env"):
            with open(filename, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            key, value = line.split("=")
                        except ValueError:
                            error += "Error: unable to parse line %s \n" % line
                            continue
                        if value != "autopush":
                            error += (
                                "Error: do not commit an env file that does "
                                "not have autopush set for all containers: %s "
                                "\n" % line
                            )
        if error:
            print(error)
            sys.exit(1)
    sys.exit(0)


def main(unused_argv):
    """Check env files do not have debugging settings.

    Args:
        unused_argv (list): currently unused.
    """
    check_env_is_autopush()


if __name__ == "__main__":
    main(sys.argv[1:])
