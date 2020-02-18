# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit test cases for module `moblab_info`."""

import subprocess
import unittest

import mock

import moblab_info


class MoblabInfoTest(unittest.TestCase):
    """Unit test case for module moblab_info"""

    def test_get_moblab_id(self):
        """Test for getting moblab id."""
        id_ = 'moblabid'
        with mock.patch('moblab_info.open', mock.mock_open(read_data=id_)):
            self.assertEqual(moblab_info.get_or_create_id(), id_)

    def test_create_moblab_id_by_another_process(self):
        """Test for trying to create a new id after another process did it."""
        id_ = 'moblabid'
        mock_read = mock.MagicMock()
        mock_read.__enter__.return_value.read.return_value = id_
        # The lock file doesn't have to be existed.
        # pylint: disable=protected-access
        moblab_info._ID_FILE_LOCK_PATH = '/tmp/moblab_id_lock'

        with mock.patch('moblab_info.open', mock.mock_open()) as m:
            # The 1st call of `open` failed, but the 2nd call is good. This
            # means another process created it, so stop creating it.
            m.side_effect = [IOError(), mock_read]
            self.assertEqual(moblab_info.get_or_create_id(), id_)

    def test_create_moblab_id_by_self(self):
        """Test for creating a new moblab id by the current process."""
        # The lock file doesn't have to be existed.
        # pylint: disable=protected-access
        moblab_info._ID_FILE_LOCK_PATH = '/tmp/moblab_id_lock'
        mock_write = mock.MagicMock()
        new_id = 'new_uuid'

        with mock.patch('moblab_info.open', mock.mock_open()) as m:
            # The 1st and 2nd call of `open` both failed, so we have to create
            # the id file.
            m.side_effect = (IOError(), IOError(), mock_write)
            with mock.patch('uuid.uuid1') as mock_uuid:
                mock_uuid.return_value.hex = new_id
                self.assertEqual(moblab_info.get_or_create_id(), new_id)
                mock_write.__enter__.return_value.write.asset_called_once_with(
                    new_id)

    def test_get_moblab_serial_number_from_vpd(self):
        """Test for getting moblab SN from system VPD."""
        sn = '1234'
        with mock.patch('subprocess.check_output') as mock_output:
            mock_output.return_value = sn
            self.assertEqual(moblab_info.get_serial_number(), sn)

    def test_get_moblab_serial_number_from_mac(self):
        """Test for getting moblab SN from MAC."""
        sn = '1234'
        runtime_error = subprocess.CalledProcessError(1, 'bad cmd', '')
        with mock.patch('subprocess.check_output') as mock_output:
            mock_output.side_effect = [runtime_error, sn]
            self.assertEqual(moblab_info.get_serial_number(), sn)

    def test_get_moblab_serial_number_no_sn(self):
        """Test for trying to get moblab SN but failed."""
        runtime_error = subprocess.CalledProcessError(1, 'bad cmd', '')
        with mock.patch('subprocess.check_output') as mock_output:
            mock_output.side_effect = runtime_error
            self.assertEqual(moblab_info.get_serial_number(),
                             moblab_info.NO_SERIAL_NUMBER)


if __name__ == '__main__':
    unittest.main()
