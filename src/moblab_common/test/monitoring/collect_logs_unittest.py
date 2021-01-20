# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the collect logs utils"""
import copy
import json
import sys
import unittest

from unittest import mock
from unittest.mock import MagicMock  # , PropertyMock

from moblab_common.monitoring.collect_logs import collect_logs

MOCKED_DOCKER = MagicMock()
sys.modules["docker"] = MOCKED_DOCKER
sys.modules["shutil"] = MagicMock()


_NUM_MOCK_CONTAINERS = 10
_MOCK_MOBLAB_ID = "mock_moblab_id"
_MOCK_CONTAINER_NAME = "mock_container"
_MOCK_CONTAINER_SUCCINCT = {
    "Command": "a",
    "Created": "b",
    "Id": "c",
    "Image": "d",
    "ImageID": "e",
    "Names": "f",
    "State": "g",
    "Status": "h",
}
_MOCK_CONTAINER_DETAILED = copy.deepcopy(_MOCK_CONTAINER_SUCCINCT)
_MOCK_CONTAINER_DETAILED.update({"OtherAttribute": "i"})
_MOCK_CONTAINERS_SUCCINCT = [
    _MOCK_CONTAINER_SUCCINCT for _ in range(_NUM_MOCK_CONTAINERS)
]
_MOCK_CONTAINERS_DETAILED = [
    _MOCK_CONTAINER_DETAILED for _ in range(_NUM_MOCK_CONTAINERS)
]

_MOCK_CONTAINER_INSPECT_DICT = {"attr1": "value1", "attr2": "value2"}

_MOCK_TEMPDIR_PATH = "/tmp/moblab_logs_xxxxxxxx/"


class CollectLogsTest(unittest.TestCase):
    """Testing the collect logs code."""

    def _create_mock_api_client(self):
        mock_api_client = MagicMock()
        mock_api_client.containers.return_value = _MOCK_CONTAINERS_DETAILED
        mock_api_client.inspect_container.return_value = (
            _MOCK_CONTAINER_INSPECT_DICT
        )
        return mock_api_client

    def _create_mock_docker_client(self):
        mock_docker_client = MagicMock()
        mock_container = MagicMock()
        mock_container.name = _MOCK_CONTAINER_NAME
        mock_docker_client.containers.list.return_value = [
            mock_container for _ in range(_NUM_MOCK_CONTAINERS)
        ]
        return mock_docker_client

    def _create_mock_host_connector(self):
        mock_host_connector = MagicMock()
        mock_host_connector.get_host_identifier.return_value = _MOCK_MOBLAB_ID
        return mock_host_connector

    @mock.patch("os.chmod")
    @mock.patch("tempfile.TemporaryDirectory")
    @mock.patch("moblab_common.monitoring.collect_logs.cli")
    @mock.patch("moblab_common.monitoring.collect_logs._write_to_file")
    @mock.patch("moblab_common.monitoring.collect_logs.docker.from_env")
    @mock.patch("moblab_common.monitoring.collect_logs.docker.APIClient")
    @mock.patch(
        "moblab_common.monitoring.collect_logs.host_connector.HostServicesConnector"
    )
    def test_collect_logs(
        self,
        mock_host_services_connector,
        mock_docker_api_client,
        mock_docker_from_env,
        mock_write_to_file,
        mock_cli,
        mock_temp_dir,
        mock_chmod,
    ):
        mock_temp_dir.return_value.__enter__.return_value = _MOCK_TEMPDIR_PATH
        mock_docker_api_client.return_value = self._create_mock_api_client()
        mock_docker_from_env.return_value = self._create_mock_docker_client()
        mock_host_services_connector.return_value = (
            self._create_mock_host_connector()
        )

        collect_logs()

        self.assertEqual(
            mock_write_to_file.call_count, 4 + _NUM_MOCK_CONTAINERS
        )
        mock_write_to_file.assert_has_calls(
            [
                mock.call(
                    _MOCK_TEMPDIR_PATH + "docker/inspect_mock_container.log",
                    json.dumps(
                        _MOCK_CONTAINER_INSPECT_DICT, indent=4, sort_keys=True
                    ),
                ),
                mock.call(
                    _MOCK_TEMPDIR_PATH + "docker/docker_ps_detailed.log",
                    json.dumps(
                        _MOCK_CONTAINERS_DETAILED, indent=4, sort_keys=True
                    ),
                ),
                mock.call(
                    _MOCK_TEMPDIR_PATH + "docker/docker_ps_succinct.log",
                    json.dumps(
                        _MOCK_CONTAINERS_SUCCINCT, indent=4, sort_keys=True
                    ),
                ),
                mock.call(_MOCK_TEMPDIR_PATH + "config", mock.ANY),
                mock.call(_MOCK_TEMPDIR_PATH + "serialno", _MOCK_MOBLAB_ID),
            ],
            any_order=True,
        )
        mock_cli.create_tarball.assert_called_once()


if __name__ == "__main__":
    unittest.main()
