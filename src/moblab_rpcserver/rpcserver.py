#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import argparse
import grpc
import logging
import os
import sys
import time

from concurrent import futures

import moblab_rpcservice
# pylint: disable=import-error
from moblab_common.proto import moblabrpc_pb2_grpc

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS',
                      '%s/.service_account.json' % os.environ['HOME'])

def setup_logging(level):
    """Enable the correct level of logging.

    Args:
        level (int): One of the predefined logging levels, e.g loging.DEBUG
    """
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(level)
    fh = logging.FileHandler('/var/log/moblab/moblab_rpc.log')
    fh.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)


def parse_arguments(argv):
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Turn on debug logging.')
    return parser.parse_args(argv)


def serve():
    options = parse_arguments(sys.argv[1:])
    logging_severity = logging.INFO
    if options.verbose:
        logging_severity = logging.DEBUG
    setup_logging(logging_severity)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=500))

    moblab_service = moblab_rpcservice.MoblabRpcService()

    try:
        moblabrpc_pb2_grpc.add_MoblabRpcServiceServicer_to_server(
            moblab_service, server)

        server.add_insecure_port('[::]:6002')
        logging.info('Starting server')
        server.start()
        while True:
            logging.info('Server sleepin')
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
