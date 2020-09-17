# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Simple layer to abstrace the grpc implementation from users.

import logging
import grpc

from host_services import hostservices_pb2
from host_services import hostservices_pb2_grpc

DEFAULT_SERVER = "dockerhost:7002"

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
                cls.stub = hostservices_pb2_grpc.MoblabHostServiceStub(
                    cls.channel)
                if not cls.stub:
                    raise HostServicesException(
                "Unable to connect to server %s" % DEFAULT_SERVER)
            else:
                raise HostServicesException(
            "No server found %s" % DEFAULT_SERVER)

    @classmethod
    def disconnect(cls):
        # Invalidate the cached connection.
        cls.channel = None
        cls.stub = None

    @classmethod
    def get_host_identifier(cls):
        # Call the host service to get a non volatile identifier.
        cls.connect()
        try:
            request = hostservices_pb2.HostIdentifierRequest()
            response = cls.stub.get_host_identifier(request)
            return response.identifier
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error getting the host identifier')
            raise HostServicesException('Error getting the host identifier')

    @classmethod
    def is_service_running(cls, service_name):
        cls.connect()
        try:
            request = hostservices_pb2.ServiceRunningRequest()
            response = cls.stub.get_host_identifier(request)
            return response.is_running
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error getting service %s status', service_name)
            raise HostServicesException('Error getting service %s status' % service_name)

    @classmethod
    def get_disk_info(cls):
        cls.connect()
        try:
            request = hostservices_pb2.DiskInfoRequest()
            response = cls.stub.get_disk_info(request)
            return response.disk_info
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error getting disk info')
            raise HostServicesException('Error getting disk info')

    @classmethod
    def get_ip(cls):
        cls.connect()
        try:
            request = hostservices_pb2.IpRequest()
            response = cls.stub.get_ip(request)
            return response.ip_address
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error getting host ip')
            raise HostServicesException('Error getting host ip')

    @classmethod
    def check_for_system_update(cls):
        cls.connect()
        try:
            request = hostservices_pb2.SystemUpdateCheckRequest()
            response = cls.stub.check_for_system_update(request)
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error checking for system updates')
            raise HostServicesException('Error checking for system updates')

    @classmethod
    def get_system_update_status(cls):
        cls.connect()
        try:
            request = hostservices_pb2.SystemUpdateStatusRequest()
            response = cls.stub.get_system_update_status(request)
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error getting update status')
            raise HostServicesException('Error getting update status')

    @classmethod
    def install_system_update(cls):
        cls.connect()
        try:
            request = hostservices_pb2.SystemUpdateInstallRequest()
            response = cls.stub.install_system_update(request)
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error installing update')
            raise HostServicesException('Error installing update')

    @classmethod
    def reboot(cls):
        cls.connect()
        try:
            request = hostservices_pb2.RebootRequest()
            response = cls.stub.reboot(request)
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error rebooting')
            raise HostServicesException('Error rebooting')

    @classmethod
    def factory_reset(cls):
        cls.connect()
        try:
            request = hostservices_pb2.FactoryResetRequest()
            response = cls.stub.factory_reset(request)
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception('Error factory reset')
            raise HostServicesException('Error factory reset')
