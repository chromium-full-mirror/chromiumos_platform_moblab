#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import argparse
import grpc.aio
import logging
import os
import sys
import asyncio

from concurrent import futures

import moblab_rpcservice
import moblab_configuration_rpcservice

from moblab_common.proto import moblabrpc_pb2
from moblab_common.proto.moblabrpc_pb2_grpc import (
    add_MoblabRpcServiceServicer_to_server,
)
from moblab_common.proto import moblab_configuration_rpc_pb2
from moblab_common.proto.moblab_configuration_rpc_pb2_grpc import (
    add_MoblabConfigurationServiceServicer_to_server,
)

from disk_space_monitor_service import DiskSpaceMonitorService

from grpc_reflection.v1alpha import reflection

os.environ.setdefault(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "%s/.service_account.json" % os.environ["HOME"],
)


def setup_logging(level):
    """Enable the correct level of logging.

    Args:
        level (int): One of the predefined logging levels, e.g loging.DEBUG
    """
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(level)
    fh = logging.FileHandler("/var/log/moblab/moblab_rpc.log")
    fh.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)


def parse_arguments(argv):
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Turn on debug logging."
    )
    return parser.parse_args(argv)


async def serve():
    options = parse_arguments(sys.argv[1:])
    logging_severity = logging.INFO
    if options.verbose:
        logging_severity = logging.DEBUG
    setup_logging(logging_severity)

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=500))
    try:
        add_MoblabRpcServiceServicer_to_server(
            moblab_rpcservice.MoblabRpcService(), server
        )

        add_MoblabConfigurationServiceServicer_to_server(
            moblab_configuration_rpcservice.ConfigurationRpcService(), server
        )

        SERVICE_NAMES = (
            moblab_configuration_rpc_pb2.DESCRIPTOR.services_by_name[
                "MoblabConfigurationService"
            ].full_name,
            moblabrpc_pb2.DESCRIPTOR.services_by_name[
                "MoblabRpcService"
            ].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

        serving_port = 6002
        server.add_insecure_port("[::]:%s" % serving_port)

        async def run_grpc_server():
            await server.start()
            logging.info("Starting server port %s" % serving_port)
            await server.wait_for_termination()

        await asyncio.gather(
            run_grpc_server(),
            DiskSpaceMonitorService().run(),
        )

    finally:
        await server.stop(0)


if __name__ == "__main__":
    asyncio.run(serve())
