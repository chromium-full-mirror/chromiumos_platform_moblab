# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple layer to abstrace the grpc host server implementation from users."""

import logging
import grpc
import grpc.aio

from moblab_common.proto import hostservice_pb2
from moblab_common.proto import hostservice_pb2_grpc

from google.protobuf import empty_pb2

DEFAULT_SERVER = "dockerhost:7002"

channel = None
stub = None


class HostServicesException(Exception):
    """Base class off all exceptions raised by this class."""

    pass


class HostServicesConnector(object):
    """Abstract away the server connect/disconnect/host/port details."""

    channel = None
    stub = None

    @classmethod
    def connect(cls):
        """Establish a connection to the grpc server.

        The connection is cached in the class variables channel and stub.

        Raises:
            HostServicesException: If there are issues connecting to the
                server.
        """
        if not cls.channel or not cls.stub:
            cls.channel = grpc.insecure_channel(DEFAULT_SERVER)
            if cls.channel:
                cls.stub = hostservice_pb2_grpc.MoblabHostServiceStub(
                    cls.channel
                )
                if not cls.stub:
                    raise HostServicesException(
                        "Unable to connect to server %s" % DEFAULT_SERVER
                    )
            else:
                raise HostServicesException(
                    "No server found %s" % DEFAULT_SERVER
                )

    @classmethod
    def disconnect(cls):
        """Clean up the cached connection, typically done on failure.

        If there cached variables are set to None then the connect function
        will attempt to re-establish the connection with the server.
        """
        # Invalidate the cached connection.
        cls.channel = None
        cls.stub = None

    @classmethod
    def get_host_identifier(cls):
        """Get a unique identifier for this particular host machine.

        This is not guaraneteed to be unique, a device may have the same
        serial number as another, but it is unlikely.

        Raises:
            HostServicesException: [description]

        Returns:
            string: A unique identifier for the host.
        """
        # Call the host service to get a non volatile identifier.
        cls.connect()
        try:
            response = cls.stub.get_host_identifier(empty_pb2.Empty())
            return response.identifier
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting the host identifier")
            raise HostServicesException("Error getting the host identifier")

    @classmethod
    def get_disk_info(cls):
        """Get debug information about disk usage.

        The format if this information can vary - do not parse the data, it is
        for debug display only.

        Raises:
            HostServicesException: if there is an issue with the host server.

        Returns:
            string: Multiline debug information about disk usage on the host.
        """
        cls.connect()
        try:
            response = cls.stub.get_disk_info(empty_pb2.Empty())
            return response.disk_info
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting disk info")
            raise HostServicesException("Error getting disk info")

    @classmethod
    def get_cpu_temperature(cls):
        cls.connect()
        try:
            response = cls.stub.get_cpu_temperature(empty_pb2.Empty())
            return response.temperature
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting cpu temperature")
            raise HostServicesException("Error getting cpu temperature")

    @classmethod
    def get_ip(cls):
        """Get the host servers external IP address.

        Raises:
            HostServicesException: if there is an issue with the host server.

        Returns:
            string: IP address of the host server.
        """
        cls.connect()
        try:
            response = cls.stub.get_ip(empty_pb2.Empty())
            return response.ip_address
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting host ip")
            raise HostServicesException("Error getting host ip")

    @classmethod
    def get_external_mac_address(cls):
        """Get the host server's external MAC address.

        Raises:
            HostServicesException: if there is an issue with the host server.

        Returns:
            string: MAC address of the host server.
        """
        cls.connect()
        try:
            response = cls.stub.get_external_mac_address(empty_pb2.Empty())
            return response.mac_address
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting host MAC address")
            raise HostServicesException("Error getting host MAC address")

    @classmethod
    def check_for_system_update(cls):
        """Check to see if the underlying host system needs to update.

        This may not be implemented on all hosts.

        Raises:
            HostServicesException: if there is an issue with the host server.
        """
        cls.connect()
        try:
            cls.stub.check_for_system_update(empty_pb2.Empty())
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error checking for system updates")
            raise HostServicesException("Error checking for system updates")

    @classmethod
    def get_system_update_status(cls):
        """If the host is updating get progress information.

        This may not be implemented on all hosts.

        Raises:
            HostServicesException: if there is an issue with the host server.

        Returns:
            SystemUpdateStatusResponse:
                string: progress, % progress message.
                string: current_op, downloading / updating etc.
                string: new_size, not currently used but new size in bytes.
                string: new_version, os update version string.
                string: last_checked_time, time last checked for update in
                    seconds since 1/1/1970
        """
        cls.connect()
        try:
            response = cls.stub.get_system_update_status(empty_pb2.Empty())
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting update status")
            raise HostServicesException("Error getting update status")

    @classmethod
    def install_system_update(cls):
        """If there is a pending update for the host, start that update.

        This may not be implemented on all hosts.

        Raises:
            HostServicesException: if there is an issue with the host server.

        Returns:
            SystemUpdateInstallResponse:
                string: error, any error messages.
        """
        cls.connect()
        try:
            response = cls.stub.install_system_update(empty_pb2.Empty())
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error installing update")
            raise HostServicesException("Error installing update")

    @classmethod
    def reboot(cls):
        """Reboot the host server.

        This may not be implemented on all hosts.

        Raises:
            HostServicesException: if there is an issue with the host server.
        """
        cls.connect()
        try:
            cls.stub.reboot(empty_pb2.Empty())
        except grpc.RpcError as e:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error rebooting")
            raise HostServicesException("Error rebooting: " + str(e))

    @classmethod
    def factory_reset(cls):
        """Reset the host device to factory defaults deleting all non os files.

        This may not be implemented on all hosts.

        Raises:
            HostServicesException: if there is an issue with the host server.
        """
        cls.connect()
        try:
            cls.stub.factory_reset(empty_pb2.Empty())
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error factory reset")
            raise HostServicesException("Error factory reset")

    @classmethod
    def get_system_version(cls):
        """Get information about the host server OS name and version.

        Raises:
            HostServicesException: if there is an issue with the host server.

        Returns:
            SystemVersionResponse:
                string: version, the version number of the host OS system.
                string: track, what track the OS is on beta/stable etc
                string: description, test description about the host OS.
        """
        cls.connect()
        try:
            response = cls.stub.get_system_version(empty_pb2.Empty())
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting version number")
            raise HostServicesException("Error getting version number")

    @classmethod
    def stop_ui(cls):
        """Stop ui of the host machine OS.

        This may not be implemented on all hosts.

        Raises:
            HostServicesException: if there is an issue with the host server.
        """
        cls.connect()
        try:
            cls.stub.stop_ui(empty_pb2.Empty())
        except grpc.RpcError as e:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error stop ui")
            raise HostServicesException("Error stop ui: " + str(e))

class AsyncHostServicesConnector(object):
    """Abstract away the server connect/disconnect/host/port details."""

    async_stub = None
    async_channel = None

    @classmethod
    def connect(cls):
        """Establish a connection to the grpc server.

        The connection is cached in the class variables channel and stub.

        Raises:
            HostServicesException: If there are issues connecting to the
                server.
        """
        if not cls.async_channel or not cls.async_stub:
            cls.async_channel = grpc.aio.insecure_channel(DEFAULT_SERVER)
            if cls.async_channel:
                cls.async_stub = hostservice_pb2_grpc.MoblabHostServiceStub(
                    cls.async_channel
                )
                if not cls.async_stub:
                    raise HostServicesException(
                        "Unable to connect to server %s" % DEFAULT_SERVER
                    )
            else:
                raise HostServicesException(
                    "No server found %s" % DEFAULT_SERVER
                )

    @classmethod
    def disconnect(cls):
        """Clean up the cached connection, typically done on failure.

        If there cached variables are set to None then the connect function
        will attempt to re-establish the connection with the server.
        """
        # Invalidate the cached connection.
        cls.async_channel = None
        cls.async_stub = None

    @classmethod
    async def get_disk_stats(cls):
        """Get the disk usage information.

        Raises:
            HostServicesException: if there is an issue with the host server.

        Returns:
            DiskUsage:
                int: available, the mount of available disk space (in MB).
                int: total, the total mount of disk space (in MB).
        """
        cls.connect()
        try:
            return await cls.async_stub.get_disk_usage_stats(empty_pb2.Empty())
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting disk usage statistics")
            raise HostServicesException("Error getting disk usage statistics")
