# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit test for the moblab configuration connector."""

import unittest
from unittest import mock
from moblab_common.moblab_configuration_connector import (
    MoblabConfigurationRpcConnector,
)
from moblab_common.proto.moblab_configuration_rpc_pb2 import (
    StableVersion,
    GetStableBuildVersionResponse,
)


class MoblabConfigurationRpcConnectorTest(unittest.TestCase):
    """Testing the moblab configuration rpc connector."""

    @mock.patch(
        "moblab_common.moblab_configuration_connector.grpc_stub.MoblabConfigurationServiceStub"
    )
    def test_get_stable_build_version_resolved(
        self, mock_moblab_configuration_service
    ):
        result = GetStableBuildVersionResponse(
            stable_version=StableVersion(
                default_version="default_version",
                override_version="override_version",
            )
        )
        mock_moblab_configuration_service.return_value.get_stable_build_version.return_value = (
            result
        )

        res = (
            MoblabConfigurationRpcConnector.get_stable_build_version_resolved(
                "board"
            )
        )
        self.assertEqual(res, "override_version")


if __name__ == "__main__":
    unittest.main()
