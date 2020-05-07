#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import argparse
import grpc

# pylint: disable=import-error
import remoteagentrpc_pb2
# pylint: disable=import-error
import remoteagentrpc_pb2_grpc

import logging

class RemoteLoggingAgent(remoteagentrpc_pb2_grpc.RemoteLoggingAgentServicer):

    def __init__(self):
        super(RemoteLoggingAgent, self).__init__()

    def hello_world(self, request, _context):
        response = moblabrpc_pb2.HelloWorldResponse(
            message="Hello World"
        return response


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

    moblab_service = MoblabRpcService()

    try:
        moblabrpc_pb2_grpc.add_MoblabRpcServiceServicer_to_server(
            moblab_service, server)

        server.add_insecure_port('[::]:6050')
        logging.info('Starting server')
        server.start()
        while True:
            logging.info('Server sleeping')
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
