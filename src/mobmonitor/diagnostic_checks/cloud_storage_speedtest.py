# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import sys

sys.path.append('..')
from abstract_diagnostic_check import AbstractDiagnosticCheck
from diagnostic_error import DiagnosticError
from util import osutils
from util import config

class CloudStorageSpeedTest(AbstractDiagnosticCheck):
    """
    Uses gsutil perfdiag to get the speed of the connection between
    moblab and the configured gs bucket
    """

    GSUTIL_USER = 'moblab'

    category = 'Cloud Storage'

    name = 'Speed Test'

    description = ('Test the speed of the connection between the moblab and the'
    ' cloud storage bucket')

    def _process_results(self, data):
        # search through the results json file to get the throughput numbers
        json_data = json.loads(data)

        download_bytes_ps = json_data['read_throughput']['bytes_per_second']
        # bytes to bits, then bps to mbps
        download_mbps = download_bytes_ps * 8 / 1000000.0

        upload_bytes_ps = json_data['write_throughput']['bytes_per_second']
        upload_mbps = upload_bytes_ps * 8 / 1000000.0

        return 'download %.4f mbps\nupload %.4f mbps' % (
                download_mbps, upload_mbps)


    def run(self):
        bucket_url = config.Config().get('image_storage_server')
        if bucket_url is None:
            raise DiagnosticError('Bucket URL is not configured')

        output_file = '/tmp/perfdiag_output.json'
        cmd = ['gsutil', 'perfdiag', '-s' '1M', '-o', output_file, bucket_url]
        try:
            osutils.sudo_run_command(cmd, user=self.GSUTIL_USER)
        except osutils.RunCommandError:
            raise DiagnosticError('Failed to run gsutil perfdiag command')

        with open(output_file, 'r') as f:
            try:
                return self._process_results(f.read())
            except:
                raise DiagnosticError('Failed to process speedtest results')
