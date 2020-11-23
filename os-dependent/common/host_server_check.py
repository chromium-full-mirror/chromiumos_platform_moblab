#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Check the host server is installed correctly and working."""

import argparse
import grpc
import hostservice_pb2_grpc
import logging

from google.protobuf import empty_pb2


def get_host_identifier(stub):
    """Check the host identifier is working."""
    try:
        print(
            "Host identifier:  %s"
            % (stub.get_host_identifier(empty_pb2.Empty())).identifier
        )
    except grpc.RpcError:
        logging.exception("Failed to get host identifier.")


def get_disk_info(stub):
    """Check the disk info is working."""
    print("Disk Info:\n%s" % stub.get_disk_info(empty_pb2.Empty()).disk_info)


def get_ip(stub):
    """Check the get IP call is working."""
    print("IP Address: %s" % stub.get_ip(empty_pb2.Empty()).ip_address)


def check_for_system_update(stub):
    """Check the system update call is working."""
    print("Calling check system update.")
    try:
        stub.check_for_system_update(empty_pb2.Empty())
    except grpc.RpcError:
        logging.exception("Failed to check for system update.")


def get_system_update_status(stub):
    """Check that system update status is begin returned."""
    try:
        status = stub.get_system_update_status(empty_pb2.Empty())
        progress = status.progress
        new_version = status.new_version
        print(
            "Update version: %s:\nUpdate progress %s" % (new_version, progress)
        )
    except grpc.RpcError:
        logging.exception("Failed to system update status.")


def install_system_update(stub):
    """Check that the command to install update works."""
    print("Install update.")
    try:
        stub.install_system_update(empty_pb2.Empty())
    except grpc.RpcError:
        logging.exception("Failed to install update.")


def reboot(stub):
    """Check that host service can reboot."""
    print("Rebooting.")
    try:
        stub.reboot(empty_pb2.Empty())
    except grpc.RpcError:
        logging.exception("Failed to reboot.")


def factory_reset(stub):
    """Check that host service can reset to factory condition."""
    print("Factory reset.")
    try:
        stub.reboot(empty_pb2.Empty())
    except grpc.RpcError:
        logging.exception("Failed to reset.")


def get_system_version(stub):
    """Check that host server is returning the system version."""
    try:
        print(stub.get_system_version(empty_pb2.Empty()))
    except grpc.RpcError:
        logging.exception("Failed to get system version.")


def get_api_version(stub):
    """Check that the api version is working."""
    print(stub.get_api_version(empty_pb2.Empty()))


if __name__ == "__main__":
    channel = grpc.insecure_channel("localhost:7002")
    stub = hostservice_pb2_grpc.MoblabHostServiceStub(channel)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update", action="store_true", help="check host update works"
    )
    parser.add_argument(
        "--reboot", action="store_true", help="check reboot works"
    )
    parser.add_argument(
        "--reset", action="store_true", help="check reset works"
    )
    args = parser.parse_args()

    get_host_identifier(stub)
    get_disk_info(stub)
    get_ip(stub)
    check_for_system_update(stub)
    get_system_update_status(stub)
    get_system_version(stub)
    get_api_version(stub)

    # This will update your moblab to the latest stable - don't do it if you
    # are not sure.  You can rollback if you do it by accident.
    if args.update:
        install_system_update(stub)

    # Reboots the device if implemented by the host server.
    if args.reboot:
        reboot(stub)

    # Resets the device back to just base OS, only implemented on chromeos.
    if args.reset:
        factory_reset(stub)
