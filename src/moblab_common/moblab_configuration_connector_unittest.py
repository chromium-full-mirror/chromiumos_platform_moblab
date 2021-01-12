# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit test for the moblab configuration connector."""

import unittest
from unittest import mock
from moblab_configuration_connector import MoblabConfigurationRpcConnector
from moblab_common.proto.moblab_configuration_rpc_pb2 import StableVersion


class MoblabConfigurationRpcConnectorTest(unittest.TestCase):
    """Testing the moblab configuration rpc connector."""

    @mock.patch(
        "moblab_common.proto.moblab_configuration_rpc_pb2_grpc."
        + "MoblabConfigurationServiceStub.get_stable_build_version"
    )
    def test_get_stable_build_version_resolved(
        self, mock_get_stable_build_version
    ):
        mock_get_stable_build_version.return_value = StableVersion(
            override_version="override_version",
            default_version="default_version",
        )
        res = (
            MoblabConfigurationRpcConnector.get_stable_build_version_resolved()
        )
        self.assertEqual(res, "override_version")


if __name__ == "__main__":
    unittest.main()
