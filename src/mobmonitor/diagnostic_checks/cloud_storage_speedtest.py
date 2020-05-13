# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
import sys

sys.path.append('..')
from .abstract_diagnostic_check import AbstractDiagnosticCheck
from .diagnostic_error import DiagnosticError
from util import osutils
from util import config

class CloudStorageSpeedTest(AbstractDiagnosticCheck):
    """
    Uses gsutil perfdiag to get the speed of the connection between
    moblab and the configured gs bucket
    """

    GSUTIL_USER = 'moblab'

    FAILURE_MESSAGE_TEMPLATE = (
        'Moblab is not configured to access Google Storage\n%s')

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
            return self.FAILURE_MESSAGE_TEMPLATE % 'No bucket is set'

        # test that the boto configuration is correct before running speedtest
        ls_cmd = ['gsutil', 'ls', '-b', bucket_url]
        try:
            osutils.sudo_run_command(ls_cmd, user=self.GSUTIL_USER)
        except osutils.RunCommandError:
            return (self.FAILURE_MESSAGE_TEMPLATE %
                "Can't connect with bucket " + bucket_url)

        output_file = '/tmp/perfdiag_output.json'
        #docker run --rm -it -e BOTO_CONFIG=/home/moblab/.boto -v default_moblab_home:/home/moblab google/cloud-sdk:alpine "gsutil perfdiag -s 1M -o /tmp/aaaa gs://chromeos-moblab-peng-staging
        perf_cmd = [
            'gsutil', 'perfdiag', '-s' '1M', '-o', output_file, bucket_url]
        try:
            osutils.sudo_run_command(perf_cmd, user=self.GSUTIL_USER)
        except osutils.RunCommandError:
            raise DiagnosticError('Failed to run gsutil perfdiag command')

        with open(output_file, 'r') as f:
            try:
                return self._process_results(f.read())
            except:
                raise DiagnosticError('Failed to process speedtest results')
