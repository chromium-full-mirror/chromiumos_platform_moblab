import io
import os
import unittest
from unittest.mock import patch
import host_server_chromeos


class HostServerChromeosTest(unittest.TestCase):
    @patch("os.popen")
    def test_get_disk_usage(self, mock_df_output):
        mock_df_output.return_value = io.StringIO(
            "/dev/mmcblk0   900000M 300000M   600000M  30% /stateful_partition"
        )
        host_services = host_server_chromeos.HostServerChromeOS()

        response = host_services.get_disk_usage_stats(None, None)
        self.assertIsNotNone(response)
