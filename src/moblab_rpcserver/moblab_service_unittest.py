# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the MoblabService"""
import sys
import unittest

from collections import namedtuple
from unittest import mock
from unittest.mock import MagicMock, PropertyMock


class MockNotFoundError(Exception):
  pass

class MockClientError(Exception):
  pass

MOCKED_DOCKER = MagicMock()
MOCKED_DOCKER.errors.NotFound = MockNotFoundError

MOCKED_GOOGLE = MagicMock()
MOCKED_GOOGLE.api_core.exceptions.ClientError = MockClientError

sys.modules['docker'] = MOCKED_DOCKER
sys.modules['google'] = MOCKED_GOOGLE
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.api_core'] = MagicMock()
sys.modules['moblab_common'] = MagicMock()
sys.modules['requests'] = MagicMock()

from moblab_service import MoblabService, MoblabRpcError


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

  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_get_usable_build_targets(self, mock_afe_connector):
    mock_afe_connector.return_value.get_connected_devices.return_value = [
        {'labels' : ['hostname:mock_dut_1', 'model:mock_model_1', 'board:mock_build_target_1']},
        {'labels' : ['hostname:mock_dut_2', 'model:mock_model_2', 'board:mock_build_target_2']},
        {'labels' : ['hostname:mock_dut_3', 'model:mock_model_1', 'board:mock_build_target_1']}
    ]
    build_targets = self.service.list_usable_build_targets('mock_model_1')
    self.assertEqual(build_targets, ['mock_build_target_1'])

  @mock.patch("moblab_service.docker.from_env")
  def test_get_is_update_available(self, mock_docker_from_env):
    mock_docker_client = MagicMock()
    # A single tagless container should cause update to show as available.
    mock_docker_client.containers.list.return_value = \
      [self._create_mock_container(['tag']) for _ in range(3)] + \
      [self._create_mock_container()]
    mock_docker_from_env.return_value = mock_docker_client

    is_update_available = self.service.get_is_update_available()
    assert(is_update_available)

  @mock.patch("moblab_service.docker.from_env")
  def test_get_is_update_not_available(self, mock_docker_from_env):
    mock_docker_client = MagicMock()
    mock_docker_client.containers.list.return_value = \
      [self._create_mock_container(['tag']) for _ in range(3)]
    mock_docker_from_env.return_value = mock_docker_client

    is_update_available = self.service.get_is_update_available()
    assert(is_update_available == False)

  @mock.patch("moblab_service.docker.from_env")
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

  @mock.patch("moblab_service.docker.from_env")
  def test_update_docker_already_running(self, mock_docker_from_env):
    mock_docker_from_env.return_value = MagicMock()

    with self.assertRaises(MoblabRpcError) as context:
      result_msg = self.service.update_docker()

  def _mock_afe_connector_methods(self, mock_afe_connector, succeed_validate, succeed_cloud_configuration_set, succeed_remote_agent_config_commit):
    if succeed_validate:
      mock_afe_connector.return_value.validate_cloud_storage_info.return_value = True, 'Cloud values validated.'
    else:
      mock_afe_connector.return_value.validate_cloud_storage_info.return_value = False, 'Cloud validation failed.'

    mock_afe_connector.return_value.set_configuration_info.return_value = succeed_cloud_configuration_set
    mock_afe_connector.return_value.set_is_remote_agent_enabled.return_value = succeed_remote_agent_config_commit

  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_set_cloud_configuration(self, mock_afe_connector):
    SetCloudConfigurationTestParams = namedtuple(
        'SetCloudConfigurationTestParams',
        [
            # Test inputs for MoblabService.set_cloud_configuration call.
            'is_cloud_enabled',
            'boto_key_id',
            'boto_key_secret',
            'gcs_bucket_url',
            'is_remote_agent_enabled',
            # The follow are bools to set whether mock afe_connector succeeds or fails for the
            # validate_cloud_storage_info, set_configuration_info, and set_is_remote_agent_enabled.
            'succeed_validate',
            'succeed_cloud_configuration_set',
            'succeed_remote_agent_config_commit',
            # Expected message to be returned by MoblabService.set_cloud_configuration
            'expected_message_output'
        ]
    )

    # below is a list of different permutations of potential inputs to set_cloud_configuration + different behaviors for
    # the mocked afe_connector. Each item includes the expected message output of the set_cloud_configuration that will
    # be assert'ed against.
    parameterized_set_cloud_configuration_tests = [
        # test completely successful set cloud config.
        SetCloudConfigurationTestParams(
            is_cloud_enabled=True,
            boto_key_id='fake-boto-id',
            boto_key_secret='fake-boto-secret',
            gcs_bucket_url='gs://bucket/',
            is_remote_agent_enabled=True,
            succeed_validate=True,
            succeed_cloud_configuration_set=True,
            succeed_remote_agent_config_commit=True,
            expected_message_output='Successfully applied cloud configuration values. Remote agent has been enabled.'
        ),
        # test set only cloud disabled.
        SetCloudConfigurationTestParams(
            is_cloud_enabled=False,
            boto_key_id=None,
            boto_key_secret=None,
            gcs_bucket_url=None,
            is_remote_agent_enabled=None,
            succeed_validate=True,
            succeed_cloud_configuration_set=True,
            succeed_remote_agent_config_commit=True,
            expected_message_output='Successfully disabled cloud configuration.'
        ),
        # test validation failed.
        SetCloudConfigurationTestParams(
            is_cloud_enabled=True,
            boto_key_id='fake-boto-id',
            boto_key_secret='fake-boto-secret',
            gcs_bucket_url='gs://bucket/',
            is_remote_agent_enabled=True,
            succeed_validate=False,
            succeed_cloud_configuration_set=True,
            succeed_remote_agent_config_commit=True,
            expected_message_output='Cloud validation failed.'
        ),
        # test cloud configuration successfully committed but remote agent toggle set failed
        SetCloudConfigurationTestParams(
            is_cloud_enabled=True,
            boto_key_id='fake-boto-id',
            boto_key_secret='fake-boto-secret',
            gcs_bucket_url='gs://bucket/',
            is_remote_agent_enabled=True,
            succeed_validate=True,
            succeed_cloud_configuration_set=True,
            succeed_remote_agent_config_commit=False,
            expected_message_output='Successfully applied cloud configuration values. But failed to set remote agent as enabled.'
        )
    ]

    for params in parameterized_set_cloud_configuration_tests:
      with self.subTest():
        self._mock_afe_connector_methods(
            mock_afe_connector,
            params.succeed_validate,
            params.succeed_cloud_configuration_set,
            params.succeed_remote_agent_config_commit
        )


        message = self.service.set_cloud_configuration(
            params.is_cloud_enabled,
            params.boto_key_id,
            params.boto_key_secret,
            params.gcs_bucket_url,
            params.is_remote_agent_enabled
        )
        print(message)
        assert(message == params.expected_message_output)

  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  @mock.patch("moblab_service.build_connector")
  @mock.patch("moblab_service.moblab_build_connector")
  def test_set_cloud_configuration_updates_build_connectors(self, mock_moblab_build_connector, mock_build_connector, mock_afe_connector):
    # Mocking setup.
    self._mock_afe_connector_methods(mock_afe_connector, True, True, True)
    # Mock and track call-throughs to re-initialize connectors.
    MockMoblabBuildConnector = MagicMock()
    mock_moblab_build_connector.MoblabBuildConnector = MockMoblabBuildConnector
    MockBuildConnector = MagicMock()
    mock_build_connector.MoblabBuildConnector = MockBuildConnector

    pre_build_connector_call_count = MockBuildConnector.call_count
    pre_moblab_build_connector_call_count = MockMoblabBuildConnector.call_count

    message = self.service.set_cloud_configuration(
        True,
        'mock-boto-key-id',
        'mock-boto-key-secret',
        'gs:/mock-gcs-url',
        True
    )

    self.service.moblab_build_connector
    self.service.build_connector

    # Verifies that, after an invokation of set_cloud_configuration, references to the two build connectors results in
    # a reinitialization of each. This ensures that changes in target bucket or service_account creds gets ingested.
    assert(MockMoblabBuildConnector.call_count == pre_moblab_build_connector_call_count + 1)
    assert(MockBuildConnector.call_count == pre_build_connector_call_count + 1)

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

  @mock.patch.object(MoblabService, 'moblab_build_connector', new_callable=PropertyMock)
  @mock.patch.object(MoblabService, 'config_connector', new_callable=PropertyMock)
  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_run_suite(self, mock_afe_connector, mock_config_connector, mock_moblab_build_connector):
    mock_config_connector.return_value.get_test_wifi_ap_and_password.return_value = ('mock_ssid', 'mock_wifi_pass')
    mock_afe_connector.return_value.run_suite.return_value = (1, None) # (job_id, error_msg)
    mock_moblab_build_connector.return_value.check_build_stage_status.side_effect = [False, True]

    self.service.run_suite(
        'mock_build_target',
        'mock_model',
        '99',
        '00000.00.0',
        'mock_suite'
    )
    mock_afe_connector.return_value.run_suite.assert_called_with(
        'mock_build_target',
        'mock_build_target-release/R99-00000.00.0',
        {'cros-version': 'mock_build_target-release/R99-00000.00.0'},
        'mock_suite',
        1440,
        None,
        'mock_model',
        suite_args={},
        test_args={'ssid': 'mock_ssid', 'wifipass': 'mock_wifi_pass'}
    )
    mock_moblab_build_connector.return_value.stage_build.assert_called_once()

  @mock.patch.object(MoblabService, 'moblab_build_connector', new_callable=PropertyMock)
  @mock.patch.object(MoblabService, 'config_connector', new_callable=PropertyMock)
  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_run_suite_afe_failure(self, mock_afe_connector, mock_config_connector, mock_moblab_build_connector):
    mock_config_connector.return_value.get_test_wifi_ap_and_password.return_value = ('mock_ssid', 'mock_wifi_pass')
    mock_afe_connector.return_value.run_suite.return_value = (None, 'Create suite job attempt failed, blah blah blah.') # (job_id, error_msg)
    mock_moblab_build_connector.return_value.check_build_stage_status.return_value = True

    with self.assertRaises(MoblabRpcError) as context:
      self.service.run_suite(
          'mock_build_target',
          'mock_model',
          '99',
          '00000.00.0',
          'mock_suite'
      )

  @mock.patch.object(MoblabService, 'build_connector', new_callable=PropertyMock)
  @mock.patch.object(MoblabService, 'moblab_build_connector', new_callable=PropertyMock)
  @mock.patch.object(MoblabService, 'config_connector', new_callable=PropertyMock)
  @mock.patch.object(MoblabService, 'afe_connector', new_callable=PropertyMock)
  def test_run_suite_api_failure(self, mock_afe_connector, mock_config_connector, mock_moblab_build_connector, mock_build_connector):
    mock_config_connector.return_value.get_test_wifi_ap_and_password.return_value = ('mock_ssid', 'mock_wifi_pass')
    mock_afe_connector.return_value.run_suite.return_value = (1, None) # (job_id, error_msg)
    mock_moblab_build_connector.return_value.check_build_stage_status.side_effect = MockClientError()
    mock_build_connector.return_value.get_builds_for_milestone.return_value = ['00000.00.0']

    self.service.run_suite(
        'mock_build_target',
        'mock_model',
        '99',
        '00000.00.0',
        'mock_suite'
    )

    mock_build_connector.return_value.get_builds_for_milestone.assert_called_once()

if __name__ == "__main__":
  unittest.main()
