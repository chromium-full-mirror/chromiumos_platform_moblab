# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import concurrent
import logging
import sys
import time

import grpc

from lab import dut_manager_storage_pb2
from lab import dut_manager_storage_pb2_grpc

_LOGGER = logging.getLogger("dut-manager-storage")


class DutManagerStorage(
    dut_manager_storage_pb2_grpc.DutManagerStorageServiceServicer
):
    def setup_logging(self, level):
        """Set up the custom file log handler.

        Logs to bootup as that is mounted in the moblab software debug
        container.

        Args:
            level (integer): A valid python logging level.
        """
        _LOGGER.setLevel(level)
        handler = logging.FileHandler(
            "/var/log/moblab/dut_manager_storage.log"
        )
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(filename)s:%(lineno)d %(levelname)s:"
                " %(message)s"
            )
        )
        # Some code runs before this function may have created some handler
        # and we don't want them.
        _LOGGER.handlers = [handler]

    def parse_arguments(self, argv):
        """Parse arguments passed to the server.

        Args:
            argv (list): Arguments passed to to the server.

        Returns:
            [type]: [description]
        """
        parser = argparse.ArgumentParser(description=__doc__)

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Turn on debug logging.",
        )
        return parser.parse_args(argv)

    def serve(self, args):
        """Run the DUT manager GRPC server.

        Args:
            args (): Parameters passed to the server.
        """
        options = self.parse_arguments(args)
        logging_severity = logging.INFO
        if options.verbose:
            logging_severity = logging.DEBUG
        self.setup_logging(logging_severity)

        server = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=500)
        )

        try:
            dut_manager_storage_pb2_grpc.add_DutManagerStorageServiceServicer_to_server(
                self, server
            )

            server.add_insecure_port("[::]:7003")
            logging.info("Starting server on 7003")
            server.start()
            while True:
                logging.info("Server sleeping")
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == "__main__":
    host_server = DutManagerStorage()
    host_server.serve(sys.argv[1:])
