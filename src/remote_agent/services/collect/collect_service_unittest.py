#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from io import StringIO
from unittest import TestCase, main
from unittest.mock import patch, call

import collect_service

from remote_agent.constants import Constants

# pylint: disable=missing-function-docstring
# pylint: disable=no-member
# pylint: disable=unused-argument
# pylint: disable=too-many-public-methods


class CollectServiceTest(TestCase, Constants):
    """Testing the CollectService code."""

    MOBLAB_IP = '100.1.1.1'
    HOST_ID = 'test_host_id'
    INSTALL_ID = 'test_install_id'
    BUCKET_NAME = 'test_bucket'
    MILESTONE = 80
    BUILD_VERSION = '10000.1.0'
    CHANNEL = 'dev-channel'
    DESCRIPTION = 'test_description'

    DUT_IP_ADDRESS_1 = '200.1.1.1'
    DUT_IP_ADDRESS_2 = '300.1.1.1'
    DUT_ID_1 = 'serial1'
    DUT_ID_2 = 'serial2'

    def _set_moblab_version_info(self, version_info):
        self.test_collect_service.afe_connector.get_version_info.return_value = version_info

    def _setup_for_test_collect_attr_for_duts(self, connected_devices, dut_ids):
        self.test_collect_service.afe_connector.get_connected_devices.return_value \
            = connected_devices
        self.test_collect_service.dut_connector.get_connected_dut_serialno.return_value = dut_ids

    def setUp(self):
        self.test_collect_service = collect_service.CollectService()
        self.test_collect_service.moblab_host_id = self.HOST_ID
        self.test_collect_service.moblab_install_id = self.INSTALL_ID
        self.test_collect_service.bucket_name = self.BUCKET_NAME
        self.test_collect_service.moblab_version_info = {
            "CHROMEOS_RELEASE_CHROME_MILESTONE": str(self.MILESTONE) + '\n',
            "CHROMEOS_RELEASE_TRACK": self.CHANNEL + '\n',
            "CHROMEOS_RELEASE_DESCRIPTION": self.DESCRIPTION + '\n',
            "MOBLAB_SERIAL_NUMBER": self.HOST_ID,
            "MOBLAB_ID": self.INSTALL_ID,
            "CHROMEOS_RELEASE_VERSION": self.BUILD_VERSION + '\n'
        }

        # mock connectors
        self.afe_connector_patcher = patch('collect_service.afe_connector.AFEConnector')
        self.dut_connector_patcher = patch('collect_service.dut_connector.MoblabDUTConnector')
        self.host_connector_patcher = patch('collect_service.host_connector.HostServicesConnector')
        self.config_connector_patcher \
            = patch('collect_service.config_connector.MoblabConfigConnector')
        mock_afe_connector = self.afe_connector_patcher.start()
        mock_dut_connector = self.dut_connector_patcher.start()
        mock_host_connector = self.host_connector_patcher.start()
        mock_config_connector = self.config_connector_patcher.start()
        self.test_collect_service.afe_connector = mock_afe_connector.return_value
        self.test_collect_service.dut_connector = mock_dut_connector.return_value
        self.test_collect_service.host_connector = mock_host_connector.return_value
        self.test_collect_service.config_connector = mock_config_connector.return_value

    def tearDown(self):
        self.afe_connector_patcher.stop()
        self.dut_connector_patcher.stop()
        self.host_connector_patcher.stop()
        self.config_connector_patcher.stop()

    @patch('collect_service.get_version_info')
    def test_collect_moblab_key_attributes_succeeds(self, mock_get_version_info):
        mock_get_version_info.return_value = self.test_collect_service.moblab_version_info
        self.test_collect_service.moblab_host_id = None
        self.test_collect_service.moblab_install_id = None

        collect_succeeds = self.test_collect_service.collect_moblab_key_attributes()

        self.assertTrue(collect_succeeds)
        self.assertEqual(self.test_collect_service.moblab_host_id, self.HOST_ID)
        self.assertEqual(self.test_collect_service.moblab_install_id, self.INSTALL_ID)

    @patch('collect_service.get_version_info')
    def test_collect_moblab_key_attributes_fails_with_key_error(self, mock_get_version_info):
        mock_get_version_info.return_value = {}

        with self.assertLogs('collect_service', level='INFO') as log:
            collect_succeeds = self.test_collect_service.collect_moblab_key_attributes()

        self.assertIn("Failed to get moblab key attributes for missing key: "
                      "'MOBLAB_SERIAL_NUMBER'", log.output[0])
        self.assertFalse(collect_succeeds)

    def test_create_moblab_basic_message_succeeds(self):
        self.test_collect_service.host_connector.get_ip.return_value = self.MOBLAB_IP

        moblab = self.test_collect_service.create_moblab_basic_message()

        self.assertEqual(moblab.milestone, self.MILESTONE)
        self.assertEqual(moblab.build_version, self.BUILD_VERSION)
        self.assertEqual(moblab.ip_address, self.MOBLAB_IP)
        self.assertEqual(moblab.channel, self.CHANNEL)
        self.assertEqual(moblab.description, self.DESCRIPTION)

    def test_create_moblab_basic_message_fails_with_none_key_attribute(self):
        self.test_collect_service.moblab_host_id = None

        with self.assertLogs('collect_service', level='INFO') as log:
            moblab = self.test_collect_service.create_moblab_basic_message()

        self.assertIsNone(moblab)
        self.assertIn("Failed to initiate moblab message because moblab_host_id is/are none.",
                      log.output[0])

    def test_create_moblab_basic_message_proceeds_with_key_error(self):
        del self.test_collect_service.moblab_version_info["CHROMEOS_RELEASE_VERSION"]

        with self.assertLogs('collect_service', level='INFO') as log:
            moblab = self.test_collect_service.create_moblab_basic_message()

        self.assertTrue(moblab.milestone, 84)
        self.assertFalse(moblab.HasField('build_version'))
        self.assertFalse(moblab.HasField('ip_address'))
        self.assertFalse(moblab.HasField('channel'))
        self.assertFalse(moblab.HasField('description'))
        self.assertIn("Failed to get moblab version attributes for missing key: "
                      "'CHROMEOS_RELEASE_VERSION'", log.output[0])

    def test_create_moblab_disk_message_succeeds(self):
        self.test_collect_service.host_connector.get_disk_info.return_value \
            = 'df -h\n' \
              '/dev/dm-1        15M   15M     0 100% /run\n' \
              '/dev/loop0      128K  128K     0 100% /run/chromeos-config\n' \
              '/dev/root       3.9G  1.4G  2.5G  36% /\n' \
              'devtmpfs         16G     0   16G   0% /dev\n' \
              '\n' \
              'lsblk\n' \
              'NAME                                                               MAJ:MIN ' \
              'RM   SIZE RO TYPE MOUNTPOINT\n' \
              'loop0                                                                7:0    ' \
              '0     4K  1 loop /run/chromeos-config\n' \
              '0  45.8G  0 disk [SWAP]\n'

        moblab = self.test_collect_service.create_moblab_disk_message()

        self.test_collect_service.host_connector.get_disk_info.assert_called_once()
        # expected used disk = 15M + 128K + 1.4G + 0 = 1519098265.6 bytes
        # expected free disk = 0 + 0 + 2.5G + 16G = 19864223744 bytes
        self.assertEqual(moblab.disk_stats.free_disk_size_bytes, 19864223744)
        self.assertEqual(moblab.disk_stats.total_disk_size_bytes, 21383322009)

    def test_create_moblab_disk_message_fails_with_none_disk_info(self):
        self.test_collect_service.host_connector.get_disk_info.return_value = None

        with self.assertLogs('collect_service', level='INFO') as log:
            moblab = self.test_collect_service.create_moblab_disk_message()

        self.assertIsNone(moblab)
        self.assertIn("Failed to get disk info for the error: 'NoneType'"
                      " object has no attribute 'split'", log.output[0])

    def test_create_moblab_disk_message_fails_with_incomplete_disk_info(self):
        self.test_collect_service.host_connector.get_disk_info.return_value \
            = 'df -h\n' \
              '/dev/dm-1        15M   15M     0 100% /run\n' \
              '/dev/root       3.9G  1.4G  2.5G  36% /\n' \
              'devtmpfs         16G  \n'

        with self.assertLogs('collect_service', level='INFO') as log:
            moblab = self.test_collect_service.create_moblab_disk_message()

        self.assertIsNone(moblab)
        self.assertIn("Disk info is incomplete: list index out of range", log.output[0])

    def test_create_moblab_disk_message_fails_with_wrong_disk_info_format(self):
        self.test_collect_service.host_connector.get_disk_info.return_value \
            = 'df -h\n' \
              '/dev/dm-1        15M   15M     0 100%' \
              '/dev/root       3.9G  1.4G  2.5G  36% /\n' \

        with self.assertLogs('collect_service', level='INFO') as log:
            moblab = self.test_collect_service.create_moblab_disk_message()

        self.assertIsNone(moblab)
        self.assertIn("Disk space calculation failed for the error: "
                      "could not convert string to float: '36%'", log.output[0])

    @patch('collect_service.run_gcloud_bucket_diagnosis')
    @patch('collect_service.open')
    def test_create_moblab_network_message_succeeds(self, mock_open, mock_run_diagnosis):
        network_diagnosis_res = '{"write_throughput": {"bytes_per_second": 1000},' \
                                '"read_throughput": {"bytes_per_second": 2000.11},' \
                                '"request_errors": 0,' \
                                '"connection_breaks": 1}'
        network_diagnosis_file = StringIO(network_diagnosis_res)
        mock_open.return_value.__enter__.return_value = network_diagnosis_file

        moblab = self.test_collect_service.create_moblab_network_message()

        self.assertEqual(moblab.network_stats.upload_bits_per_second, 8000)
        self.assertEqual(moblab.network_stats.download_bits_per_second, 16000)
        self.assertEqual(moblab.network_stats.server_errors, 0)
        self.assertEqual(moblab.network_stats.broken_connections, 1)

    def test_create_moblab_network_message_fails_with_no_cloud_bucket(self):
        self.test_collect_service.bucket_name = None

        with self.assertLogs('collect_service', level='INFO') as log:
            moblab = self.test_collect_service.create_moblab_network_message()

        self.assertIsNone(moblab)
        self.assertIn("Failed to initiate moblab message because bucket_name is/are none.",
                      log.output[0])

    @patch('collect_service.run_gcloud_bucket_diagnosis')
    def test_create_moblab_network_message_fails_to_get_network_stats(self, mock_run_diagnosis):
        mock_run_diagnosis.side_effect = collect_service.RunCommandError(1, 'bad_cmd')

        with self.assertLogs('collect_service', level='INFO') as log:
            moblab = self.test_collect_service.create_moblab_network_message()

        self.assertIsNone(moblab)
        self.assertIn("Failed to get network status from network diagonosis: Command 'bad_cmd'"
                      " returned non-zero exit status 1.", log.output[0])

    def test_create_dut_basic_message_succeeds_with_all_attributes(self):
        labels = ['cts_cpu_x86', 'board:test_board', 'model:test_model']
        dut_info_dict = {
            'labels': labels,
            'locked': True,
            'lock_reason': 'test_reason'
        }

        dut = self.test_collect_service.create_dut_basic_message(dut_info_dict, self.DUT_ID_1)

        self.assertEqual(dut.build_target, 'test_board')
        self.assertEqual(dut.model, 'test_model')
        self.assertEqual(dut.label, labels)
        self.assertTrue(dut.is_locked)
        self.assertEqual(dut.lock_reason, 'test_reason')

    def test_create_dut_basic_message_succeeds_without_some_attributes(self):
        labels = ['cts_cpu_x86', 'model:test_model']
        dut_info_dict = {
            'labels': labels,
            'locked': False,
            'lock_reason': ''
        }

        dut = self.test_collect_service.create_dut_basic_message(dut_info_dict, self.DUT_ID_1)

        self.assertFalse(dut.HasField('build_target'))
        self.assertEqual(dut.model, 'test_model')
        self.assertEqual(dut.label, labels)
        self.assertFalse(dut.is_locked)
        self.assertFalse(dut.HasField('lock_reason'))

    def test_create_dut_status_message_succeeds(self):
        dut_info_dict = {'status': 'Repair Failed'}
        dut = self.test_collect_service.create_dut_status_message(dut_info_dict, self.DUT_ID_1)
        self.assertEqual(dut.status, 4) # enum DutStatus { DUT_STATUS_REPAIR_FAILED = 4;}

    def test_create_dut_status_message_fails_with_unrecorded_status(self):
        dut_info_dict = {'status': 'Unrecorded'}

        with self.assertLogs('collect_service', level='INFO') as log:
            dut = self.test_collect_service.create_dut_status_message(dut_info_dict, self.DUT_ID_1)

        self.assertIn("Unrecorded dut status: Enum DutStatus has no value defined for "
                      "name DUT_STATUS_UNRECORDED", log.output[0])
        self.assertIsNone(dut)

    @patch('collect_service.CollectService.collect_moblab_key_attributes')
    @patch('collect_service.CollectService.create_moblab_disk_message')
    def test_collect_attr_for_moblab_succeeds_with_disk_attribute(self, mock_disk_msg,
                                                                  mock_key_attr):
        mock_disk_msg.return_value = collect_service.remoteagentrpc_pb2.MoblabHost()

        moblab = self.test_collect_service.collect_attr_for_moblab('DISK')
        mock_key_attr.assert_called_once()
        mock_disk_msg.assert_called_once()
        self.assertTrue(moblab.HasField('last_update_time'))

    @patch('collect_service.CollectService.collect_moblab_key_attributes')
    def test_collect_attr_for_moblab_fails_with_unknown_attribute_type(self, mock_key_attr):
        with self.assertLogs('collect_service', level='INFO') as log:
            moblab = self.test_collect_service.collect_attr_for_moblab('UNKNOWN_TYPE_MOBLAB')

        self.assertIn("Moblab does not have attribute type: UNKNOWN_TYPE_MOBLAB", log.output[0])
        self.assertIsNone(moblab)

    @patch('collect_service.CollectService.collect_moblab_key_attributes')
    @patch('collect_service.CollectService.create_dut_status_message')
    @patch('collect_service.CollectService.create_dut_basic_message')
    def test_collect_attr_for_duts_succeeds(self, dut_basic, dut_status, mock_key_attr):
        dut_basic.return_value = collect_service.remoteagentrpc_pb2.MoblabDut()
        device_one = {
            'hostname': self.DUT_IP_ADDRESS_1,
            'id': 1,
            'labels': ['board:octopus', 'model:caroline']
        }
        device_two = {
            'hostname': self.DUT_IP_ADDRESS_2,
            'id': 2,
            'labels': []
        }
        connected_devices = [device_one, device_two]
        dut_ids = [(self.DUT_IP_ADDRESS_2, self.DUT_ID_2), (self.DUT_IP_ADDRESS_1, self.DUT_ID_1)]
        self._setup_for_test_collect_attr_for_duts(connected_devices=connected_devices,
                                                   dut_ids=dut_ids)

        duts = self.test_collect_service.collect_attr_for_duts('DUT_BASIC')

        mock_key_attr.assert_called_once()
        calls = [call(device_one, self.DUT_ID_1), call(device_two, self.DUT_ID_2)]
        dut_basic.assert_has_calls(calls, any_order=True)
        self.assertEqual(dut_basic.call_count, 2)
        dut_status.assert_not_called()
        self.assertEqual(len(duts), 2)

    @patch('collect_service.CollectService.collect_moblab_key_attributes')
    def test_collect_attr_for_duts_fails_with_none_dut_ids(self, mock_key_attr):
        self._setup_for_test_collect_attr_for_duts(
            connected_devices=[{'hostname': self.DUT_IP_ADDRESS_1}],
            dut_ids=None
        )

        with self.assertLogs('collect_service', level='INFO') as log:
            duts = self.test_collect_service.collect_attr_for_duts('DUT_BASIC')

        self.assertEqual(duts, [])
        self.assertIn('Dut serial numbers or connected devices list is empty/none.', log.output[0])

    @patch('collect_service.CollectService.collect_moblab_key_attributes')
    def test_collect_attr_for_duts_fails_with_unknown_attribute_type(self, mock_key_attr):
        self._setup_for_test_collect_attr_for_duts(
            connected_devices=[{'hostname': self.DUT_IP_ADDRESS_1}],
            dut_ids=[(self.DUT_IP_ADDRESS_1, self.DUT_ID_1)]
        )

        with self.assertLogs('collect_service', level='INFO') as log:
            duts = self.test_collect_service.collect_attr_for_duts('UNKNOWN_TYPE_DUT')

        self.assertEqual(duts, [])
        self.assertIn("Dut does not have attribute type: UNKNOWN_TYPE_DUT", log.output[0])

    @patch('collect_service.CollectService.collect_moblab_key_attributes')
    def test_collect_attr_for_duts_returns_empty_list_with_unmatched_hostnames(self, mock_key_attr):
        self._setup_for_test_collect_attr_for_duts(
            connected_devices=[{'hostname': self.DUT_IP_ADDRESS_1}],
            dut_ids=[(self.DUT_IP_ADDRESS_2, self.DUT_ID_2)]
        )

        self.assertEqual(self.test_collect_service.collect_attr_for_duts('DUT_STATUS'), [])


if __name__ == '__main__':
    main()
