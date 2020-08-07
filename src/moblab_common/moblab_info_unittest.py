# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit test cases for module `moblab_info`."""

import os
import sys
import subprocess
import unittest
import mock

from unittest.mock import MagicMock


# To make moblab_common imports work.
sys.path.insert(0, os.path.dirname(__file__).rsplit('/', 1)[0])
sys.modules['host_services'] = MagicMock()
from moblab_common.host_connector import HostServicesException
sys.modules['moblab_common.host_connector'] = MagicMock()
sys.modules['moblab_common.lock_util'] = MagicMock()

import moblab_info


MOCK_IP = '0.0.0.0'
MOCK_ID = '6fcecb39f90348d68ea684280ffe8fbf'
MOCK_SERIAL_NO = 'KKPVLWAI60246530'
MOCK_ETC_LSB_RELEASE_COMPLETE = [
    "CHROMEOS_RELEASE_BUILDER_PATH=fizz-moblab-release/R84-13099.19.0",
    "CHROMEOS_RELEASE_NAME=Chrome OS",
]
MOCK_ETC_LSB_RELEASE_INCOMPLETE = [
    "CHROMEOS_RELEASE_NAME=Chrome OS",
]

MOCK_VERSION_INFO = {
    'CHROMEOS_RELEASE_BUILDER_PATH': 'fizz-moblab-release/R84-13099.19.0',
    'CHROMEOS_RELEASE_NAME': 'Chrome OS',
    'CHROMEOS_RELEASE_VERSION': 'R84-13099.19.0',
    'MOBLAB_ID': MOCK_ID,
    'MOBLAB_SERIAL_NUMBER': MOCK_SERIAL_NO
}


class MoblabInfoTest(unittest.TestCase):
    """Unit test case for module moblab_info"""

    def test_get_moblab_id(self):
        """Test for getting moblab id."""
        id_ = "moblabid"
        with mock.patch("moblab_info.open", mock.mock_open(read_data=id_)):
            self.assertEqual(moblab_info.get_or_create_id(), id_)

    def test_create_moblab_id_by_another_process(self):
        """Test for trying to create a new id after another process did it."""
        id_ = "moblabid"
        mock_read = mock.MagicMock()
        mock_read.__enter__.return_value.read.return_value = id_
        # The lock file doesn't have to be existed.
        # pylint: disable=protected-access
        moblab_info._ID_FILE_LOCK_PATH = "/tmp/moblab_id_lock"

        with mock.patch("moblab_info.open", mock.mock_open()) as m:
            # The 1st call of `open` failed, but the 2nd call is good. This
            # means another process created it, so stop creating it.
            m.side_effect = [IOError(), mock_read]
            self.assertEqual(moblab_info.get_or_create_id(), id_)

    def test_create_moblab_id_by_self(self):
        """Test for creating a new moblab id by the current process."""
        # The lock file doesn't have to be existed.
        # pylint: disable=protected-access
        moblab_info._ID_FILE_LOCK_PATH = "/tmp/moblab_id_lock"
        mock_write = mock.MagicMock()
        new_id = "new_uuid"

        with mock.patch("moblab_info.open", mock.mock_open()) as m:
            # The 1st and 2nd call of `open` both failed, so we have to create
            # the id file.
            m.side_effect = (IOError(), IOError(), mock_write)
            with mock.patch("uuid.uuid1") as mock_uuid:
                mock_uuid.return_value.hex = new_id
                self.assertEqual(moblab_info.get_or_create_id(), new_id)
                mock_write.__enter__.return_value.write.asset_called_once_with(new_id)

    @mock.patch('moblab_info.host_connector.HostServicesConnector.get_host_identifier')
    def test_get_moblab_serial_number_from_vpd(self, mock_get_host_identifier):
        """Test for getting moblab SN from system VPD."""
        mock_get_host_identifier.return_value = MOCK_SERIAL_NO

        with mock.patch("subprocess.check_output") as mock_output:
            self.assertEqual(moblab_info.get_serial_number(), MOCK_SERIAL_NO)

    @mock.patch('moblab_info.host_connector.HostServicesConnector.get_host_identifier')
    def test_get_moblab_serial_number_from_mac(self, mock_get_host_identifier):
        """Test for getting moblab SN from MAC."""
        mock_get_host_identifier.return_value = MOCK_SERIAL_NO

        runtime_error = subprocess.CalledProcessError(1, "bad cmd", "")
        with mock.patch("subprocess.check_output") as mock_output:
            self.assertEqual(moblab_info.get_serial_number(), MOCK_SERIAL_NO)

    @mock.patch('moblab_info.host_connector.HostServicesConnector.get_host_identifier')
    def test_get_moblab_serial_number_no_sn(self, mock_get_host_identifier):
        """Test for trying to get moblab SN but failed."""
        mock_get_host_identifier.side_effect = [HostServicesException]

        self.assertEqual(
            moblab_info.get_serial_number(), moblab_info.NO_SERIAL_NUMBER
        )

    @mock.patch('moblab_info.host_connector.HostServicesConnector.get_ip')
    def test_get_network_info(self, mock_get_ip):
        mock_get_ip.return_value = MOCK_IP

        self.assertEqual(
            moblab_info.get_network_info(),
            {'server_ip': MOCK_IP, 'is_connected': True}
        )

    @mock.patch('moblab_info.host_connector.HostServicesConnector.get_ip')
    def test_get_network_info_failed(self, mock_get_ip):
        mock_get_ip.side_effect = [HostServicesException]

        self.assertEqual(
            moblab_info.get_network_info(),
            {'server_ip': None, 'is_connected': False}
        )

    def _get_mock_file(self, src_lsb_release):
        mock_file = MagicMock()
        mock_file.readlines.return_value = src_lsb_release
        mock_file.__enter__.return_value.read.return_value = MOCK_ID
        return mock_file

    @mock.patch('moblab_info.host_connector.HostServicesConnector.get_host_identifier')
    @mock.patch('builtins.open')
    def test_get_version_info(self, mock_open, mock_get_host_identifier):
        mock_open.return_value = self._get_mock_file(MOCK_ETC_LSB_RELEASE_COMPLETE)
        mock_get_host_identifier.return_value = MOCK_SERIAL_NO

        self.assertEqual(
            moblab_info.get_version_info(),
            MOCK_VERSION_INFO
        )

    @mock.patch('moblab_info.host_connector.HostServicesConnector.get_host_identifier')
    @mock.patch('builtins.open')
    def test_get_version_info_failed(self, mock_open, mock_get_host_identifier):
        mock_open.return_value = self._get_mock_file(MOCK_ETC_LSB_RELEASE_INCOMPLETE)
        mock_get_host_identifier.return_value = MOCK_SERIAL_NO


        with self.assertLogs('moblab_info', level='INFO') as log:
            self.assertRaises(
                moblab_info.MoblabInfoError,
                moblab_info.get_version_info
            )
            self.assertIn(
                "Unable to parse ChromeOS release version.",
                log.output[0]
            )


if __name__ == "__main__":
    unittest.main()
