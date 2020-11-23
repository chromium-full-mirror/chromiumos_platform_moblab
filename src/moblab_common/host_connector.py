# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Simple layer to abstrace the grpc host server implementation from users."""

import logging
import grpc

from moblab_common.proto import hostservice_pb2
from moblab_common.proto import hostservice_pb2_grpc

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
            request = hostservice_pb2.HostIdentifierRequest()
            response = cls.stub.get_host_identifier(request)
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
            request = hostservice_pb2.DiskInfoRequest()
            response = cls.stub.get_disk_info(request)
            return response.disk_info
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting disk info")
            raise HostServicesException("Error getting disk info")

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
            request = hostservice_pb2.IpRequest()
            response = cls.stub.get_ip(request)
            return response.ip_address
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting host ip")
            raise HostServicesException("Error getting host ip")

    @classmethod
    def check_for_system_update(cls):
        """Check to see if the underlying host system needs to update.

        This may not be implemented on all hosts.

        Raises:
            HostServicesException: if there is an issue with the host server.
        """
        cls.connect()
        try:
            request = hostservice_pb2.SystemUpdateCheckRequest()
            cls.stub.check_for_system_update(request)
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
            request = hostservice_pb2.SystemUpdateStatusRequest()
            response = cls.stub.get_system_update_status(request)
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
            request = hostservice_pb2.SystemUpdateInstallRequest()
            response = cls.stub.install_system_update(request)
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
            request = hostservice_pb2.RebootRequest()
            cls.stub.reboot(request)
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error rebooting")
            raise HostServicesException("Error rebooting")

    @classmethod
    def factory_reset(cls):
        """Reset the host device to factory defaults deleting all non os files.

        This may not be implemented on all hosts.

        Raises:
            HostServicesException: if there is an issue with the host server.
        """
        cls.connect()
        try:
            request = hostservice_pb2.FactoryResetRequest()
            cls.stub.factory_reset(request)
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
            request = hostservice_pb2.SystemVersionRequest()
            response = cls.stub.get_system_version(request)
            return response
        except grpc.RpcError:
            cls.disconnect()  # Force reconnect on retry
            logging.exception("Error getting version number")
            raise HostServicesException("Error getting version number")
