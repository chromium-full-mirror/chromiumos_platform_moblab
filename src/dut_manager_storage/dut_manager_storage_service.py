# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import re
from datetime import datetime

from google.protobuf import timestamp_pb2

from constants import (
    AFE_SPECIAL_TASK_TO_DUT_STATUS_MAPPINGS,
    AFE_TO_DUT_STATUS_MAPPINGS,
)
from lab import dut_manager_storage_pb2
from lab.managed_dut_pb2 import (
    ManagedDut,
    Pool,
    HistoryRecord,
    NetworkIdentifier,
    Lock,
)
from chromiumos.test.api.dut_attribute_pb2 import (
    DutAttribute,
    DutAttributeList,
)
from chromiumos.config.api import mfg_config_id_pb2
from chromiumos.storage_path_pb2 import StoragePath
from moblab_common import afe_connector


class DutManagerStorageService(object):
    """Class that implements the storage service which interacts with the db.

    This will be the layer that directly interact with the database for the
    managed DUTS.
    """

    pool_re = re.compile(r"^pool:(.*)")
    storage_path_re = re.compile(r"^cros-version:(.*)")
    tags_re = re.compile(r"(.*):(.*)")

    def __init__(self):
        """Initialize the connector that interacts with autotest afe server."""
        self.afe_connector = afe_connector.AFEConnector()

    def create_managed_dut(self, dut):
        """Enroll the given dut using the dut name through autotest afe."""
        dut_identifier = (
            dut.name.ip_address
            if dut.name.HasField("ip_address")
            else dut.name.hostname
        )
        self.afe_connector.enroll_duts([dut_identifier])

    def delete_managed_dut(self, dut_name):
        """Unenroll the given dut through autotest afe."""
        self.afe_connector.unenroll_duts([dut_name])

    def list_managed_duts(self):
        """Get all managed duts by mapping the afe hosts to managed dut."""
        connected_duts = self.afe_connector.get_connected_devices()
        managed_duts = self.get_managed_duts_from_host_dict(connected_duts)
        return managed_duts if managed_duts else None

    def get_managed_dut(self, dut_name):
        """Get the managed dut by mapping the afe hosts to managed dut."""
        connected_dut = self.afe_connector.get_connected_devices(
            hostname=dut_name
        )
        managed_duts = self.get_managed_duts_from_host_dict(connected_dut)
        return managed_duts[0] if managed_duts else None

    def update_dut(self, dut, field_to_update):
        pass

    def get_managed_duts_from_host_dict(self, duts):
        managed_duts = []

        for dut in duts:
            labels = dut.get("labels", [])
            managed_dut = ManagedDut(
                name=NetworkIdentifier(ip_address=dut["hostname"]),
                display_name="",
                tag=self.get_dut_attributes_from_labels(self.tags_re, labels),
                pool=self.get_pools_from_labels(labels),
                peripheral=None,
                mfg_config_id=None,
                provisioned_build=self.get_provisioned_build_from_labels(
                    labels
                ),
                state=AFE_TO_DUT_STATUS_MAPPINGS[dut["status"]],
                lock=Lock(reason=dut["lock_reason"]),
                operator_notes="",
                provisioned_firmware_version="",
                history=self.get_history_record_from_special_tasks(
                    dut["hostname"]
                ),
                associated_dut=None,
                is_associated_dut=None,
            )
            managed_duts.append(managed_dut)

        return managed_duts

    def get_pools_from_labels(self, labels):
        pool_names = self.extract_value_from_labels(self.pool_re, labels)
        return [Pool(name=pool_name) for pool_name in pool_names]

    def get_provisioned_build_from_labels(self, labels):
        path = self.extract_value_from_labels(self.storage_path_re, labels)
        path = path[0] if path else ""
        host = StoragePath.HostType.GS
        return StoragePath(path=path, host_type=host)

    def get_dut_attributes_from_labels(self, pattern, labels):
        tags = [
            DutAttribute(
                id=DutAttribute.Id(value=m.group(1)), field_path=m.group(2)
            )
            for m in [pattern.match(label) for label in labels]
            if m
        ]
        return DutAttributeList(dut_attributes=tags)

    def get_history_record_from_special_tasks(self, dut_name):
        history_record = []
        try:
            dut_id = self.afe_connector.get_connected_devices(
                hostname=dut_name
            )[0]["id"]
            tasks = self.afe_connector.get_special_tasks(host_id_list=[dut_id])
            for task in tasks:
                dut_history = HistoryRecord(
                    state=self.get_history_record_state_from_dut_task(task),
                    start_time=self.get_timestamp_from_datetime_str(
                        task.get("time_started", "")
                    ),
                    end_time=self.get_timestamp_from_datetime_str(
                        task.get("time_finished", "")
                    ),
                    note="",
                    lease_owner="",
                )
                history_record.append(dut_history)
        except (IndexError, KeyError):
            logging.error("Unable to find AFE id for dut: {}".format(dut_id))

        return history_record

    def extract_value_from_labels(self, pattern, labels):
        result = [
            m.group(1) for m in [pattern.match(label) for label in labels] if m
        ]
        return list(set(result))

    def get_timestamp_from_datetime_str(self, time_str):
        if not time_str:
            return None

        dt_ts = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        tp_proto = timestamp_pb2.Timestamp()
        tp_proto.FromDatetime(dt_ts)
        return tp_proto

    def get_history_record_state_from_dut_task(self, task):
        if task["is_complete"] and not task["success"]:
            return ManagedDut.ManagedState.FAILED
        return AFE_SPECIAL_TASK_TO_DUT_STATUS_MAPPINGS[task.get("task", "")]
