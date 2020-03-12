# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Simple layer to abstrace the grpc implementation from users.

import logging
import grpc

from host_services import hostservices_pb2
from host_services import hostservices_pb2_grpc

DEFAULT_SERVER = 'dockerhost:7002'

channel = None
stub = None


class HostServicesException(Exception):
    pass


class HostServicesConnector(object):

    channel = None
    stub = None

    @classmethod
    def connect(cls):
        # Connect to the rpc service and cache the connection.
        if not cls.channel or not cls.stub:
            cls.channel = grpc.insecure_channel(DEFAULT_SERVER)
            if cls.channel:
                cls.stub = hostservices_pb2_grpc.MoblabHostServiceStub(cls.channel)
                if not cls.stub:
                    raise HostServicesException('Unable to connect to server %s', DEFAULT_SERVER)
            else:
                raise HostServicesException('No server found %s', DEFAULT_SERVER)

    @classmethod
    def disconnect(cls):
        # Invalidate the cached connection.
        cls.channel = None
        cls.stub = None

    @classmethod
    def get_host_identifier(cls):
        # Call the host service to get a non volitile identifier.
        cls.connect()
        try:
            request = hostservices_pb2.HostIdentifierRequest()
            response = cls.stub.get_host_identifier(request)
            return response.identifier
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error getting the host identifier')
            raise HostServicesException('Error getting the host identifier')
