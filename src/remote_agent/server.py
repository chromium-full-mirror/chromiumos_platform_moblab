#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import sys

from concurrent import futures

import logging
import grpc

# pylint: disable=import-error
import remoteagentrpc_pb2_grpc

from services.scheduler.scheduler import Scheduler


class RemoteLoggingAgent(remoteagentrpc_pb2_grpc.RemoteLoggingAgentServicer):

    def __init__(self):
        super(RemoteLoggingAgent, self).__init__()


def setup_logging(level):
    """Enable the correct level of logging.

    Args:
        level (int): One of the predefined logging levels, e.g loging.DEBUG.
    """
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(level)
    file_handler = logging.FileHandler('/var/log/moblab/remote_agent.log')
    file_handler.setLevel(level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)


def parse_arguments(argv):
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Turn on debug logging.')
    return parser.parse_args(argv)


def serve():
    """Starts the moblab remote agent server."""
    options = parse_arguments(sys.argv[1:])
    logging_severity = logging.INFO
    if options.verbose:
        logging_severity = logging.DEBUG
    setup_logging(logging_severity)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=500))

    remoteLoggingAgent = RemoteLoggingAgent()

    remoteagentrpc_pb2_grpc.add_RemoteLoggingAgentServicer_to_server(
        remoteLoggingAgent, server)

    server.add_insecure_port('[::]:6050')
    logging.info('Starting server')
    server.start()

    scheduler = Scheduler()
    scheduler.schedule()


if __name__ == '__main__':
    serve()
