# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Base class of the grpc server provides access to limited host os functions.

Moblab software and perhaps other dockerbox software needs access to certain
host os functionality that is not easy / possible in a container.

For each OS that moblab software is running on a concrete definition of this
service should be running on the host OS, not in a container.

Not all functionality needs to be implemented, not implementing a function
will just result in a loss of functionality in the Moblab UI or CPCon example
if reboot is not implemented the reboot button will be present but not do
anything.  If you do not implement host identifier CPCon will think all results
come from a single host machine.
"""
import argparse
import concurrent.futures
import logging
import time

import grpc

import hostservice_pb2
import hostservice_pb2_grpc

_LOGGER = logging.getLogger("host-server")


class HostServerBase(hostservice_pb2_grpc.MoblabHostServiceServicer):
    """Base class that defines the interface from moblab to the host OS.

    To allow moblab software to run on many different OS's each OS
    implements this interface.
    """

    def get_host_identifier(self, unused_request, context):
        """Return a machine identifier that should be unique and stable.

        Example: machine serial number.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def get_disk_info(self, unused_request, context):
        """Return a string that shows information about disk usage.

        This string is displayed in mobmonitor and no guarantee of the format
        is given so it should not be parsed by the client.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def get_cpu_temperature(self, unused_request, context):
        """Return a float that shows information about average CPU temperature.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def get_ip(self, unused_request, context):
        """Get the host machines IP address on the network.

        Find the address the host machine connects to the internet and
        return that value.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def get_external_mac_address(self, unused_request, context):
        """Return the external interface's ip address.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def check_for_system_update(self, unused_request, context):
        """Check to see if there is a host os update available.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def get_system_update_status(self, unused_request, context):
        """If a system update is downloading/applying get the status.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def install_system_update(self, unused_request, context):
        """If there is an update for the host os, install it.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def reboot(self, unused_request, context):
        """Reboot the host machine.

        This is an optionally implemented method to reboot the host os
        device.  Integrators into a new OS can decide if it is appropriate
        for moblab software to be allowed to reboot the host.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def factory_reset(self, unused_request, context):
        """Reset the the host machine - delete all non os data.

        This is an optionally implemented method to reset the device to the
        state it first booted as a clean OS.
        Integrators into a new OS can decide if it is appropriate
        for moblab software to be allowed to reset the host.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def get_system_version(self, unused_request, context):
        """Get version string of the host machines OS.

        Raises: NotImplementedError
        """
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "Not Implemented")
        raise NotImplementedError

    def get_api_version(self, unused_request, unused_context):
        """Get the API version number.

        To make it easier to extend the API, clients can check the
        version number to know if a new function will be present or not.

        Returns:
            GetApiVersionResponse: with version number of the interface.
        """
        response = hostservice_pb2.GetApiVersionResponse()
        response.version = 2
        return response

    def setup_logging(self, level):
        """Set up the custom file log handler.

        Logs to bootup as that is mounted in the moblab software debug
        container.

        Args:
            level (integer): A valid python logging level.
        """
        _LOGGER.setLevel(level)
        handler = logging.FileHandler("/var/log/bootup/hostservices.log")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(filename)s:%(lineno)d %(levelname)s:"
                " %(message)s"
            )
        )
        # Some code runs before this function may have created some handler
        # and we don't want them.
        _LOGGER.handlers = [handler]

    def parse_arguments(self, argv):
        """Parse arguments passed to the server.

        Args:
            argv (list): Arguments passed to to the server.

        Returns:
            [type]: [description]
        """
        parser = argparse.ArgumentParser(description=__doc__)

        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Turn on debug logging.",
        )
        return parser.parse_args(argv)

    def serve(self, args):
        """Run the host GRPC server.

        Args:
            args (): Parameteres passed to the server.
        """
        options = self.parse_arguments(args)
        logging_severity = logging.INFO
        if options.verbose:
            logging_severity = logging.DEBUG
        self.setup_logging(logging_severity)

        server = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=500)
        )

        try:
            hostservice_pb2_grpc.add_MoblabHostServiceServicer_to_server(
                self, server
            )

            server.add_insecure_port("[::]:7002")
            _LOGGER.info("Starting server on 7002")
            server.start()
            while True:
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            server.stop(0)

    def get_disk_usage_stats(self, request, context):
        """Get information about available disk space.

        Raises: NotImplementedError
        """
        raise NotImplementedError


class DiskSpaceException(Exception):
    """Exception thrown by get_disk_space endpoint."""

    pass
