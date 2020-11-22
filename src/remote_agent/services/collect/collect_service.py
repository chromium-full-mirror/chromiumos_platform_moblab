#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import subprocess
import time
import logging
import json

from moblab_common.proto import remoteagentrpc_pb2

from constants import Constants
from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common import dut_connector
from moblab_common import host_connector
from moblab_common.moblab_info import get_version_info
from moblab_common.utils.cli import (
    run_gcloud_bucket_diagnosis,
    RunCommandError,
)

# pylint: disable=no-member
# pylint: disable=no-self-use


_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CollectService(Constants):
    """Class that collects data about moblab and its connected, enrolled duts.

    Attributes:
        afe_connector: A connector to retrieve moblab and dut data from
            AFE RPC server.
        config_connector: A connector to retrieve moblab bucket name
            from autotest configuration settings.
        host_connector: A connector to retrieve moblab ip and disk stats
            from the grpc server of host services.
        dut_connector: A connector to retrieve dut serial numbers from
            AFE RPC server.
        moblab_version_info: A dictionary of moblab version info obtained from afe connector.
        moblab_host_id: The host id of moblab.
        moblab_install_id: The install id of moblab.
        bucket_name: The google storage cloud bucket name.
    """

    def __init__(self):
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector
        )
        self.host_connector = host_connector.HostServicesConnector()
        self.dut_connector = dut_connector.MoblabDUTConnector()
        self.moblab_version_info = None
        self.moblab_host_id = None
        self.moblab_install_id = None
        self.bucket_name = None

    # TODO(chromium:1116710):Rewrite unit test for this function because the way of getting
    # cloud bucket name is changed.
    def collect_moblab_key_attributes(self):
        """Collects the required attributes shared by moblab and duts.

        Returns:
            A bool indicating whether the function has successfully
            collected key attributes.
        """
        cloud_storage_info = self.afe_connector.get_cloud_storage_info()
        try:
            bucket = cloud_storage_info["image_storage_server"][5:-1]
        except KeyError:
            _LOGGER.exception(
                "Failed to get moblab key attributes because"
                " could bucket is not fetched."
            )
            return False

        if bucket:
            self.bucket_name = bucket
        else:
            _LOGGER.exception(
                "Failed to get moblab key attributes because"
                " cloud bucket name is wrong."
            )
            return False

        try:
            self.moblab_version_info = get_version_info()
            self.moblab_host_id = self.moblab_version_info[
                self.MOBLAB_HOST_ID_NAME
            ].rstrip()
            self.moblab_install_id = self.moblab_version_info[
                self.MOBLAB_INSTALL_ID_NAME
            ].rstrip()
            return True
        except KeyError as err:
            _LOGGER.exception(
                "Failed to get moblab key attributes for missing key: %s", err
            )
        return False

    def _initiate_moblab_message(self):
        """Creates an initial moblab message with required attributes.

        Returns: A MoblabHost protobuf message instance.
        """
        if None in (
            self.moblab_host_id,
            self.moblab_install_id,
            self.bucket_name,
        ):
            err_msg_1 = (
                " moblab_host_id" if self.moblab_host_id is None else ""
            )
            err_msg_2 = (
                " moblab_install_id" if self.moblab_install_id is None else ""
            )
            err_msg_3 = " bucket_name" if self.bucket_name is None else ""
            _LOGGER.exception(
                "Failed to initiate moblab message because"
                "%s%s%s is/are none.",
                err_msg_1,
                err_msg_2,
                err_msg_3,
            )
            return None

        moblab = remoteagentrpc_pb2.MoblabHost()
        moblab.moblab_host_id = self.moblab_host_id
        moblab.moblab_install_id = self.moblab_install_id
        moblab.bucket_name = self.bucket_name
        return moblab

    def create_moblab_basic_message(self):
        # TODO(chromium:1106420): Capture the outputs of 'docker ps' and
        # 'docker images' in moblab masic message.
        """Creates a basic type moblab message.

        Returns: A MoblabHost protobuf message instance.
        """
        moblab = self._initiate_moblab_message()
        if moblab is None:
            return None

        try:
            moblab.milestone = int(
                self.moblab_version_info[self.MILESTONE_NAME].rstrip()
            )
            moblab.build_version = self.moblab_version_info[
                self.BUILD_VERSION_NAME
            ].rstrip()
            moblab.ip_address = self.host_connector.get_ip()
            moblab.channel = self.moblab_version_info[
                self.CHANNEL_NAME
            ].rstrip()
            moblab.description = self.moblab_version_info[
                self.DESCRIPTION_NAME
            ].rstrip()
        except KeyError as err:
            _LOGGER.exception(
                "Failed to get moblab version attributes for missing key: %s",
                err,
            )
        return moblab

    def _calculate_disk_in_bytes(self, disk_space_list):
        """Calculates total disk space in bytes.

        Sums up the elements in a given list of disk space to obtain
        total disk space.

        Args:
            disk_space_list: A list of disk space represented by string.
                For example:
                    ['50G', '0', '2.8K', '10M', '0.5T']

        Returns:
            The sum of disk space in bytes; -1 if caclulation fails.
        """
        result = 0
        try:
            for disk_space in disk_space_list:
                if disk_space[-1] == "T":
                    result += float(disk_space[:-1]) * (2 ** 40)
                elif disk_space[-1] == "G":
                    result += float(disk_space[:-1]) * (2 ** 30)
                elif disk_space[-1] == "M":
                    result += float(disk_space[:-1]) * (2 ** 20)
                elif disk_space[-1] == "K":
                    result += float(disk_space[:-1]) * (2 ** 10)
                else:
                    result += float(disk_space)
        except ValueError as err:
            _LOGGER.exception(
                "Disk space calculation failed for the error: %s", err
            )
            raise
        return int(result)

    def _get_disk_stats(self):
        """Obtains the sizes of used disk and free disk from the host connector.

        Returns:
            A protobuf DiskStats message containing total disk size and
            free disk size info.
        """
        try:
            disk_info_str = self.host_connector.get_disk_info()
            disk_space_info = disk_info_str.split("lsblk")[0].split()
            used_disk_list = []
            available_disk_list = []
            for i in range(2, int(len(disk_space_info)), 6):
                used_disk_list.append(disk_space_info[i + 2])
                available_disk_list.append(disk_space_info[i + 3])

            used_disk_size_bytes = self._calculate_disk_in_bytes(
                used_disk_list
            )
            free_disk_size_bytes = self._calculate_disk_in_bytes(
                available_disk_list
            )

            disk_stats = remoteagentrpc_pb2.DiskStats()
            disk_stats.free_disk_size_bytes = free_disk_size_bytes
            disk_stats.total_disk_size_bytes = (
                used_disk_size_bytes + free_disk_size_bytes
            )
            return disk_stats

        except AttributeError as err:
            _LOGGER.exception("Failed to get disk info for the error: %s", err)
        except IndexError as err:
            _LOGGER.exception("Disk info is incomplete: %s", err)
        except ValueError as err:
            _LOGGER.exception("Disk info has wrong format: %s", err)
        return None

    def create_moblab_disk_message(self):
        """Creates a moblab message containing disk information.

        Returns:
            A MoblabHost protobuf message instance, or None if disk stats data is not found.
        """
        disk_stats = self._get_disk_stats()
        if disk_stats is None:
            return None

        moblab = self._initiate_moblab_message()
        if moblab is None:
            return None

        moblab.disk_stats.free_disk_size_bytes = (
            disk_stats.free_disk_size_bytes
        )
        moblab.disk_stats.total_disk_size_bytes = (
            disk_stats.total_disk_size_bytes
        )
        return moblab

    def create_moblab_network_message(self):
        """Creates a moblab message containing network information.

        Returns:
            A MoblabHost protobuf message instance, or None if moblab cloud bucket is not set
            or network diagnosis fails.
        """
        moblab = self._initiate_moblab_message()
        if moblab is None:
            return None

        try:
            output_file = "/moblab/output.json"
            run_gcloud_bucket_diagnosis(output_file, self.bucket_name)

            with open(output_file) as output:
                network_json = json.load(output)
            moblab.network_stats.upload_bits_per_second = int(
                network_json["write_throughput"]["bytes_per_second"] * 8
            )
            moblab.network_stats.download_bits_per_second = int(
                network_json["read_throughput"]["bytes_per_second"] * 8
            )
            moblab.network_stats.server_errors = network_json["request_errors"]
            moblab.network_stats.broken_connections = network_json[
                "connection_breaks"
            ]
            return moblab

        except (RunCommandError, KeyError) as err:
            _LOGGER.exception(
                "Failed to get network status from network diagonosis: %s", err
            )
            return None

    def _initiate_dut_message(self, dut_id):
        """Creates an initial dut message with required attributes.

        Returns: A MoblabDut protobuf message instance.
        """
        if None in (
            self.moblab_host_id,
            self.moblab_install_id,
            self.bucket_name,
        ):
            err_msg_1 = (
                " moblab_host_id" if self.moblab_host_id is None else ""
            )
            err_msg_2 = (
                " moblab_install_id" if self.moblab_install_id is None else ""
            )
            err_msg_3 = " bucket_name" if self.bucket_name is None else ""
            _LOGGER.exception(
                "Failed to initiate dut message because" "%s%s%s is/are none.",
                err_msg_1,
                err_msg_2,
                err_msg_3,
            )
            return None

        moblab_dut = remoteagentrpc_pb2.MoblabDut()
        moblab_dut.moblab_host_id = self.moblab_host_id
        moblab_dut.moblab_install_id = self.moblab_install_id
        moblab_dut.moblab_dut_id = dut_id
        moblab_dut.bucket_name = self.bucket_name
        return moblab_dut

    def _get_attribute_from_labels(self, attr, labels):
        """Obtains an attribute value from dut labels.

        Args:
            attr: The name of the attribute.
            labels: A list of dut labels. For example:
                ['board:octopus',
                 'model:caroline',
                 'cts_cpu_x86',
                 'cts_abi_x86',
                 'os:cros']

        Returns:
            Attribute value.
        """
        for label in labels:
            label_parts = label.split(":")
            if attr == label_parts[0]:
                if len(label_parts) > 1:
                    return label_parts[1]
                return label_parts[0]
        return None

    def create_dut_basic_message(self, dut_info_dict, dut_id):
        """Creates a basic type dut message.

        Args:
            dut_info_dict: A dictionary conainting dut info.
            dut_id: The dut id.

        Returns:
            A MoblabDut protobuf message instance.
        """
        moblab_dut = self._initiate_dut_message(dut_id)
        if moblab_dut is None:
            return None

        if len(dut_info_dict["labels"]) > 0:
            build_target = self._get_attribute_from_labels(
                "board", dut_info_dict["labels"]
            )
            model = self._get_attribute_from_labels(
                "model", dut_info_dict["labels"]
            )
            if build_target:
                moblab_dut.build_target = build_target
            if model:
                moblab_dut.model = model
            moblab_dut.label.extend(dut_info_dict["labels"])
        moblab_dut.is_locked = dut_info_dict["locked"]
        if moblab_dut.is_locked:
            moblab_dut.lock_reason = dut_info_dict["lock_reason"]

        return moblab_dut

    def create_dut_status_message(self, dut_info_dict, dut_id):
        """Creates a dut message containing dut status information.

        Args:
            dut_info_dict: A dictionary conainting dut info.
            dut_id: The dut id

        Returns:
            A MoblabDut protobuf message instance, or None if the given dut
            status is unrecorded.
        """
        moblab_dut = self._initiate_dut_message(dut_id)
        if moblab_dut is None:
            return None

        try:
            moblab_dut.status = remoteagentrpc_pb2.DutStatus.Value(
                "DUT_STATUS_{}".format(
                    dut_info_dict["status"].upper().replace(" ", "_")
                )
            )
        except ValueError as err:
            _LOGGER.exception("Unrecorded dut status: %s", err)
            return None

        return moblab_dut

    def collect_attr_for_moblab(self, attribute_type):
        """Collects moblab information related the given attribute type.

        Args:
            attribute_type: The type of moblab info we want to collect. The
                attribute types include 'MOBLAB_BASIC', 'DISK' and 'NETWORK'.

        Returns:
            A MoblabHost protobuf message instance containing moblab attributes
            that belong to the given attribute type.
        """
        moblab = None

        if not self.collect_moblab_key_attributes():
            return None

        message_attributes = {
            "MOBLAB_BASIC": self.create_moblab_basic_message,
            "DISK": self.create_moblab_disk_message,
            "NETWORK": self.create_moblab_network_message,
        }
        if attribute_type in message_attributes:
            moblab = message_attributes[attribute_type]()
            if moblab:
                moblab.last_update_time = round(
                    time.time() * 1000
                )  # in millisecond
        else:
            _LOGGER.exception(
                "Moblab does not have attribute type: %s", attribute_type
            )

        return moblab

    def collect_attr_for_duts(self, attribute_type):
        """Collects duts(connected and enrolled) information related to the given attribute type.

        Args:
            attribute_type: The type of dut info we want to collect.
                The attribute types include 'DUT_BASIC' and 'DUT_STATUS'.

        Returns:
            A list of MoblabDut protobuf message instances containing dut
            attributes that belong to the given attribute type.
        """
        duts = []

        if not self.collect_moblab_key_attributes():
            return duts

        # Obtains two lists containing different information about all connected duts. For example:
        #   moblab_dut_ids = [('192.168.231.19', '0QSK91'), ('192.168.231.11', '0QSK91')]
        #   connected_devices = [{'hostname': '192.168.231.11', 'labels': [], 'status': 'Running'},
        #                        {'hostname': '192.168.231.19', 'labels': [], 'status': 'Ready'}]
        moblab_dut_ids = self.dut_connector.get_connected_dut_serialno()
        connected_devices = self.afe_connector.get_connected_devices()

        if (
            not connected_devices
            or len(connected_devices) == 0
            or not moblab_dut_ids
            or len(moblab_dut_ids) == 0
        ):
            _LOGGER.exception(
                "Dut serial numbers or connected devices list is empty/none."
            )
            return duts

        message_attributes = {
            "DUT_BASIC": self.create_dut_basic_message,
            "DUT_STATUS": self.create_dut_status_message,
        }

        if attribute_type not in message_attributes:
            _LOGGER.exception(
                "Dut does not have attribute type: %s", attribute_type
            )
            return duts

        create_msg_func = message_attributes[attribute_type]

        moblab_duts_ids_map = {}
        for dut in moblab_dut_ids:
            # dut[0] is the dut ip, dut[1] is the dut id
            if dut[1]:
                moblab_duts_ids_map[dut[0]] = dut[1]

        if not moblab_duts_ids_map:
            return duts

        for dut_info_dict in connected_devices:
            dut_ip = dut_info_dict["hostname"]
            if dut_ip in moblab_duts_ids_map:
                dut_id = moblab_duts_ids_map[dut_ip]
                dut = create_msg_func(dut_info_dict, dut_id)
                if dut:
                    dut.ip_address = dut_ip
                    dut.last_update_time = round(
                        time.time() * 1000
                    )  # in millisecond
                    duts.append(dut)

        return duts
