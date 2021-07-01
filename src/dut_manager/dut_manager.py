# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import concurrent
import logging
import sys
import time
import os
import grpc

from dut_manager_rpcservice import DutManagerRpcService
from lab import dut_manager_pb2_grpc

_LOGGER = logging.getLogger("dut-manager")


class DutManager:
    def setup_logging(self, level, log_filename):
        """Set up the custom file log handler.

        Logs to bootup as that is mounted in the moblab software debug
        container.

        Args:
            level (integer): A valid python logging level.
        """
        _LOGGER.setLevel(level)
        if log_filename:
            handler = logging.FileHandler(log_filename)
        else:
            handler = logging.StreamHandler()
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
            "-p",
            "--grpc_port",
            help="Grpc port to run the server on.",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Turn on debug logging.",
        )
        parser.add_argument(
            "-l",
            "--logfile",
            type=str,
            required=False,
            help="Full path to logfile. By default will log to console.",
        )
        return parser.parse_args(argv)

    def serve(self, args):
        """Run the DUT manager GRPC server.

        Args:
            args (): Parameters passed to the server.
        """
        options = self.parse_arguments(args)
        logging_severity = logging.INFO

        # Environment variables take presedence over parameters
        # so that the values can be overriden in compose file

        verbose_logging = os.getenv("DEBUG_LOGS")
        if verbose_logging or options.verbose:
            logging_severity = logging.DEBUG

        # Logs to console if file is not configured
        logfile = os.environ.get("LOGFILE") or options.logfile
        self.setup_logging(logging_severity, logfile)

        server = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=500)
        )

        port = os.getenv("GRPC_SERVER_PORT") or options.grpc_port
        if not port:
            raise argparse.ArgumentError("Port is a required argument!")

        dut_manager = DutManagerRpcService()
        try:
            dut_manager_pb2_grpc.add_DutManagerServiceServicer_to_server(
                dut_manager, server
            )

            server.add_insecure_port("[::]:%s" % port)
            _LOGGER.info("Starting server on %s", port)
            server.start()
            while True:
                _LOGGER.info("Server sleeping")
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == "__main__":
    host_server = DutManager()
    host_server.serve(sys.argv[1:])
