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

import test_lab_wiring_rpcservice

from chromiumos.config.api.test.tls.wiring_pb2_grpc import (
    add_WiringServicer_to_server,
)

_LOGGER = logging.getLogger("test-lab-wiring")


class TestLabWiring(object):
    """Class that implements the test lab wiring RPC server."""

    def setup_logging(self, level):
        """Set up the custom file log handler.

        Logs to bootup as that is mounted in the moblab software debug
        container.

        Args:
            level (integer): A valid python logging level.
        """
        _LOGGER.setLevel(level)
        handler = logging.FileHandler(
            "/var/log/moblab/test-lab-wiring.log"
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
        """Run the test lab wiring GRPC server.

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

        servicer = test_lab_wiring_rpcservice.TestLabWiringRpcService()

        try:
            add_WiringServicer_to_server(servicer, server)

            server.add_insecure_port("[::]:7005")
            logging.info("Starting server on 7005")
            server.start()
            while True:
                logging.info("Server sleeping")
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == "__main__":
    host_server = TestLabWiring()
    host_server.serve(sys.argv[1:])
