# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the MoblabService"""
import sys
import unittest

from unittest import mock
from unittest.mock import MagicMock, PropertyMock


class MockNotFoundError(Exception):
  pass


MOCKED_DOCKER = MagicMock()
MOCKED_DOCKER.errors.NotFound = MockNotFoundError
sys.modules['docker'] = MOCKED_DOCKER
sys.modules['moblab_common'] = MagicMock()

from moblab_rpcservice import MoblabService, MoblabRpcError


class MoblabRPCServiceTest(unittest.TestCase):
  """Testing the MoblabService code."""

  def setUp(self):
    self.service = MoblabService()

  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_get_dut_wifi_info(self, mock_afe_connector):
    afe_get_dut_wifi_mock = MagicMock()
    mock_afe_connector.return_value.get_dut_wifi_info = afe_get_dut_wifi_mock

    self.service.get_dut_wifi_info()

    afe_get_dut_wifi_mock.assert_called_once()

  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_set_dut_wifi_info(self, mock_afe_connector):
    afe_set_configuration_info_mock = MagicMock()
    mock_afe_connector.return_value.set_configuration_info = afe_set_configuration_info_mock

    result_msg = self.service.set_dut_wifi_info(
        'Fake Wifi Name',
        'Fake Wifi Pass'
    )

    afe_set_configuration_info_mock.assert_called_once()
    assert isinstance(result_msg, str)

  def _create_mock_container(self, tags=[]):
    mock_container = MagicMock()
    mock_container.image.__str__.return_value = 'gcr.io/chromeos-partner-moblab/mock-moblab-image'
    mock_container.image.tags = tags
    return mock_container

  @mock.patch("moblab_rpcservice.docker.from_env")
  def test_get_is_update_available(self, mock_docker_from_env):
    mock_docker_client = MagicMock()
    # A single tagless container should cause update to show as available.
    mock_docker_client.containers.list.return_value = \
      [self._create_mock_container(['tag']) for _ in range(3)] + \
      [self._create_mock_container()]
    mock_docker_from_env.return_value = mock_docker_client

    is_update_available = self.service.get_is_update_available()
    assert(is_update_available)

  @mock.patch("moblab_rpcservice.docker.from_env")
  def test_get_is_update_not_available(self, mock_docker_from_env):
    mock_docker_client = MagicMock()
    mock_docker_client.containers.list.return_value = \
      [self._create_mock_container(['tag']) for _ in range(3)]
    mock_docker_from_env.return_value = mock_docker_client

    is_update_available = self.service.get_is_update_available()
    assert(is_update_available == False)

  @mock.patch("moblab_rpcservice.docker.from_env")
  def test_update_docker(self, mock_docker_from_env):
    mock_docker_client = MagicMock()
    mock_container_run = MagicMock()
    mock_docker_client.containers.get.side_effect = [MockNotFoundError]
    mock_docker_client.containers.run = mock_container_run
    mock_docker_from_env.return_value = mock_docker_client

    result_msg = self.service.update_docker()

    mock_container_run.assert_called_once_with(
        'gcr.io/chromeos-partner-moblab/watchtower:release',
        command='--run-once',
        detach=True,
        name='update',
        volumes=['/var/run/docker.sock:/var/run/docker.sock']
    )

    assert(result_msg == 'Update finished.')

  @mock.patch("moblab_rpcservice.docker.from_env")
  def test_update_docker_already_running(self, mock_docker_from_env):
    mock_docker_from_env.return_value = MagicMock()

    with self.assertRaises(MoblabRpcError) as context:
      result_msg = self.service.update_docker()

  @mock.patch.object(MoblabService, 'config_connector',
                     new_callable=PropertyMock)
  def test_get_is_remote_agent_enabled(self, mock_config_connector):
    config_get_is_remote_agent_enabled_mock = MagicMock()
    mock_config_connector.return_value.get_is_remote_agent_enabled = \
      config_get_is_remote_agent_enabled_mock

    self.service.get_is_remote_agent_enabled()

    config_get_is_remote_agent_enabled_mock.assert_called_once()

  @mock.patch.object(MoblabService, 'afe_connector',
                     new_callable=PropertyMock)
  def test_set_is_remote_agent_enabled(self, mock_afe_connector):
    afe_set_is_remote_agent_enabled_mock = MagicMock()
    mock_afe_connector.return_value.set_is_remote_agent_enabled = \
      afe_set_is_remote_agent_enabled_mock

    self.service.set_is_remote_agent_enabled(True)

    afe_set_is_remote_agent_enabled_mock.assert_called_once()


if __name__ == "__main__":
  unittest.main()
