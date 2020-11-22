# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Simple layer to abstrace the grpc implementation from users.

import logging
import grpc

from moblab_common.proto import moblabrpc_pb2
from moblab_common.proto import moblabrpc_pb2_grpc

DEFAULT_SERVER = "moblab-rpcserver:6002"

channel = None
stub = None


class MoblabRpcException(Exception):
    pass


class MoblabRpcConnector(object):

    channel = None
    stub = None

    @classmethod
    def connect(cls):
        # Connect to the rpc service and cache the connection.
        if not cls.channel or not cls.stub:
            cls.channel = grpc.insecure_channel(DEFAULT_SERVER)
            if cls.channel:
                cls.stub = moblabrpc_pb2_grpc.MoblabRpcServiceStub(cls.channel)
                if not cls.stub:
                    raise MoblabRpcException(
                        "Unable to connect to server %s" % DEFAULT_SERVER
                    )
            else:
                raise MoblabRpcException("No server found %s" % DEFAULT_SERVER)

    @classmethod
    def disconnect(cls):
        # Invalidate the cached connection.
        cls.channel = None
        cls.stub = None

    @classmethod
    def run_suite(
        cls, build_target, model, milestone, build_version, suite, pool=None
    ):
        # Call the host service to get a non volatile identifier.
        cls.connect()
        try:
            request = moblabrpc_pb2.RunSuiteRequest()
            request.suite = suite
            request.build_target = build_target
            request.milestone = milestone
            request.build_version = build_version
            request.model = model
            if pool:
                request.pool = pool
            response = cls.stub.run_suite(request)
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error calling run_suite")
            raise MoblabRpcException("Error calling run_suite")
