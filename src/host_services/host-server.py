#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import concurrent.futures
import grpc
import logging
import subprocess
import sys
import time

# pylint: disable=import-error
import hostservices_pb2
# pylint: disable=import-error
import hostservices_pb2_grpc


class HostService(hostservices_pb2_grpc.MoblabHostServiceServicer):

    def get_host_identifier(self, request, context):
        response = hostservices_pb2.HostIdentifierResponse()
        response.identifier = 'NoSerialNumber'
        for vpd_key in ['serial_number', 'ethernet_mac']:
            try:
                cmd_result = subprocess.run(['vpd', '-g', vpd_key],
                                            stdout=subprocess.PIPE)
                if (cmd_result and cmd_result.returncode == 0 and
                        cmd_result.stdout):
                    response.identifier = cmd_result.stdout
                    break
            except subprocess.SubprocessError:
                logging.exception('Error retrieving vpd value %s' % vpd_key)
        return response


def setup_logging(level):
    """Enable the correct level of logging.

    Args:
        level (int): One of the predefined logging levels, e.g loging.DEBUG
    """
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(level)
    fh = logging.FileHandler('/var/log/moblab/hostservices.log')
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

    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=500))

    host_service = HostService()

    try:
        hostservices_pb2_grpc.add_MoblabHostServiceServicer_to_server(
            host_service, server)

        server.add_insecure_port('[::]:7002')
        logging.info('Starting server')
        server.start()
        while True:
            logging.info('Server sleepin')
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
