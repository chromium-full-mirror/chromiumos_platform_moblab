# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import docker
import json
import logging
import sys

from .abstract_diagnostic_check import AbstractDiagnosticCheck
from .diagnostic_error import DiagnosticError

from moblab_common import afe_connector
from moblab_common import config_connector


sys.path.append("..")


class CloudStorageSpeedTest(AbstractDiagnosticCheck):
    """
    Uses gsutil perfdiag to get the speed of the connection between
    moblab and the configured gs bucket
    """

    GSUTIL_USER = "moblab"

    FAILURE_MESSAGE_TEMPLATE = (
        "Moblab is not configured to access Google Storage\n%s"
    )

    category = "Cloud Storage"

    name = "Speed Test"

    description = (
        "Test the speed of the connection between the moblab and the"
        " cloud storage bucket"
    )

    def _process_results(self, data):
        # search through the results json file to get the throughput numbers
        json_data = json.loads(data)

        download_bytes_ps = json_data["read_throughput"]["bytes_per_second"]
        # bytes to bits, then bps to mbps
        download_mbps = download_bytes_ps * 8 / 1000000.0

        upload_bytes_ps = json_data["write_throughput"]["bytes_per_second"]
        upload_mbps = upload_bytes_ps * 8 / 1000000.0

        return "download %.4f mbps\nupload %.4f mbps" % (
            download_mbps,
            upload_mbps,
        )

    def _run_gsutil_cmd(self, container_name, commands):
        client = docker.from_env(timeout=300)
        client.images.pull("google/cloud-sdk:alpine")

        try:
            c = client.containers.get(container_name)
            c.stop()
            c.remove()
        except docker.errors.NotFound:
            pass

        result = None
        error = None
        statuscode = None
        c = client.containers.run(
            "google/cloud-sdk:alpine",
            volumes=["default_moblab_home:/root"],
            name=container_name,
            detach=True,
            command="sleep 36000",
        )
        for command in commands:
            logging.debug(command)
            statuscode, output = c.exec_run(command)
            output = output.decode("utf-8")
            logging.debug(output)
            logging.debug(statuscode)

        c.stop()
        c.remove()
        return (statuscode, output)

    def run(self):
        afe = afe_connector.AFEConnector()
        conf = config_connector.MoblabConfigConnector(afe)
        conf.load_config()
        bucket_url = "gs://%s" % conf.get_cloud_bucket()
        if bucket_url is None:
            return self.FAILURE_MESSAGE_TEMPLATE % "No bucket is set"
        (statuscode, output) = self._run_gsutil_cmd(
            "mobmonitor-cloudcheck-ls", ["gsutil ls -b %s" % bucket_url]
        )
        if statuscode != 0:
            return (
                self.FAILURE_MESSAGE_TEMPLATE % "Can't connect with bucket "
                + bucket_url
                + " "
                + output
            )

        output_file = "/tmp/perfdiag_output.json"

        client = docker.from_env(timeout=300)
        try:
            client.containers.get("mobmonitor-cloudcheck-ls").remove()
        except docker.errors.NotFound:
            pass

        (statuscode, output) = self._run_gsutil_cmd(
            "mobmonitor-cloudcheck-perf",
            [
                "gsutil perfdiag -o out.json -s 40M %s" % bucket_url,
                "cat /out.json",
            ],
        )
        if statuscode != 0:
            raise DiagnosticError(
                "Failed to run gsutil perfdiag command %s" % output
            )

        try:
            return self._process_results(output)
        except:
            raise DiagnosticError("Failed to process speedtest results")
