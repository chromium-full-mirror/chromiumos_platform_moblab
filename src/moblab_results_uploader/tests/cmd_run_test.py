# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Test cases for module `cmd_run`."""
from __future__ import print_function

import argparse
import os
import tempfile

from unittest import mock

import pytest

import cmd_run
import gs_api_wrapper


def test_arg_parsing():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    cmd_run.add_arguments(subparsers)

    with pytest.raises(SystemExit):
        parser.parse_args(
            [cmd_run.SUB_COMMAND_NAME, "--credentials-file", "non-exist-file"]
        )

    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        args = parser.parse_args(
            [
                cmd_run.SUB_COMMAND_NAME,
                "--gs-bucket",
                "",
                "--credentials-file",
                tmp_file.name,
            ]
        )
        assert args.credentials_file == tmp_file.name

        os.environ[gs_api_wrapper.ENV_GOOGLE_APP_CREDENTIALS] = tmp_file.name
        args = parser.parse_args(
            [
                cmd_run.SUB_COMMAND_NAME,
                "--gs-bucket",
                "",
                "--credentials-file",
                tmp_file.name,
            ]
        )
        assert args.credentials_file == tmp_file.name

        args = parser.parse_args(
            [
                cmd_run.SUB_COMMAND_NAME,
                "--gs-bucket",
                "test",
                "--credentials-file",
                tmp_file.name,
                "--dry-run",
            ]
        )
        with mock.patch("gs_api_wrapper.GsApiWrapper") as m_gs_api:
            m_gs_api.side_effect = gs_api_wrapper.GsAccessError
            with pytest.raises(SystemExit):
                args.post_parse_args(args)

            m_gs_api.side_effect = None
            args.post_parse_args(args)
            assert args.gs_api is not None
            assert not hasattr(args, "gs_bucket")
            assert not hasattr(args, "credentials_file")

            assert args.once  # Set by --dry-run option implicitly.
