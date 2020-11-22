#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import time
import logging
import json
import random

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from enum import Enum

import psutil
import yaml

from constants import Constants
from services.collect.collect_service import CollectService
from services.upload.message_handler import MessageHandler
from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common.utils.cli import (
    run_gcloud_bucket_diagnosis,
    RunCommandError,
)

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)
RUNNING = True
SECONDS_IN_MIN = 60


class NoneCloudBucketException(Exception):
    pass


class Frequency(Enum):
    """Enum class that defines the levels of collection frequencies."""

    DEFAULT = 1
    WARNING = 2
    ALERT = 3


class Scheduler(Constants):
    """Class that schedules the collection and upload frequency of remote agent.

    Attributes:
        config: A map to store the scheduler configuration obtained from
            the configuration YAML file.
        collect_service: A CollectService instance to collect moblab and
            duts data.
        upload_service: A MessageHandler instance to publish moblabd and
            duts pubsub messages to CPCon.
        freq_level: A Enum representing the collection frequency level, DEFAULT,
            WARNING, or ALERT, that the collectors should follow.
        moblab_attr_types: A list of moblab attribute types.
        dut_attr_types: A list of dut attribute types.
    """

    def __init__(self):
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector
        )
        self.config = self._get_scheduler_config()
        self.collect_service = CollectService()
        self.upload_service = MessageHandler()
        self.freq_level = Frequency.DEFAULT
        self.moblab_attr_types = [self.MOBLAB_BASIC, self.DISK, self.NETWORK]
        self.dut_attr_types = [self.DUT_BASIC, self.DUT_STATUS]

    def _get_scheduler_config(self):
        """Obtains the scheduler configuration from the configuration YAML file.

        Returns:
            A map representing the scheduler configuration.
        """
        with open(self.SCHEDULER_CONFIG_PATH) as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    def collect_and_upload(self, msg_type, attr_type):
        """Collects and uploads moblab or duts data at the required frequency.

        Checks the update of the required collection frequency level every
        minute and adjusts the actual collection and upload frequency
        accordingly.

        Args:
            msg_type: A string representing the message type of the data to be
                collected, either 'moblab' or 'dut'.
            attr_type: A string representing the attribute type of the data to be
                collected. Attribute types include 'MOBLAB_BASIC', 'DISK',
                'NETWORK', 'DUT_BASIC', and 'DUT_STATUS'.
        """
        if msg_type == self.MOBLAB:
            collect_func = self.collect_service.collect_attr_for_moblab
        elif msg_type == self.DUT:
            collect_func = self.collect_service.collect_attr_for_duts
        else:
            _LOGGER.exception(
                "Wrong message type, %s. "
                "Message type should be 'moblab' or 'dut'.",
                msg_type,
            )
            return

        while RUNNING:
            # Checks if the remote agent is enabled. If not enabled, sleep
            # 1 minute and then check again.
            is_enabled = self.config_connector.get_is_remote_agent_enabled()
            if not is_enabled:
                time.sleep(SECONDS_IN_MIN)
                continue

            try:
                device_attrs = collect_func(attr_type)
            except Exception:
                _LOGGER.exception("Failed to collect Moblab or DUT data.")
                return

            if not isinstance(device_attrs, list):
                device_attrs = [device_attrs]

            if device_attrs and len(device_attrs) > 0 and device_attrs[0]:
                self.upload_service.upload_messages(device_attrs, attr_type)
            else:
                _LOGGER.info("No device info is collected or uploaded.")

            current_freq_level = self.freq_level.name
            collection_interval_in_minute = (
                self._get_attr_type_freq_with_random_factor(attr_type)
            )
            minutes_passed = 0

            while minutes_passed < collection_interval_in_minute:
                time.sleep(SECONDS_IN_MIN)
                if current_freq_level != self.freq_level.name:
                    current_freq_level = self.freq_level.name
                    collection_interval_in_minute = (
                        self._get_attr_type_freq_with_random_factor(attr_type)
                    )
                minutes_passed += 1

    def _get_attr_type_freq_with_random_factor(self, attr_type):
        """
        Gets the collection frequency with a random factor for the given
        attribute type, which can avoid all Moblabs in a lab sending data at the
        same time. A random factor should be small so that it won't affect
        the target frequency too much. The range of a random factor is
        [0, min(10% of current freq, 60)] minutes.

        Args:
            attr_type: A string representing the attribute type of the data to
                be collected. Attribute types include 'MOBLAB_BASIC', 'DISK',
                'NETWORK', 'DUT_BASIC', and 'DUT_STATUS'.

        Returns:
            A collection frequency with a random factor.
        """
        current_freq = self.config["collectors"][attr_type]["frequency"][
            self.freq_level.name
        ]
        return current_freq + random.randint(
            0, min(int(current_freq / 10), SECONDS_IN_MIN)
        )

    # TODO(chromium:1116710):Rewrite unit test for this function because the way of getting
    # cloud bucket name is changed.
    def update_freq_level(self, update_function, update_interval_minute):
        """Updates the value of the freq_level attribute.

        Args:
            update_function: The update function to update the collection
            frequency.
            update_interval_minute: An int representing the time interval of
            frequency update in minute.

        Updates the required scheduler frequency level every update_interval
        minutes.
        """
        while RUNNING:
            self.freq_level = update_function()
            time.sleep(SECONDS_IN_MIN * update_interval_minute)

    def _get_freq_based_on_network_stats(self):
        """Obtains a scheduler frequency level that suits the current network
            status.

        Returns:
            A Frequency enum.
        """
        cloud_storage_info = (
            self.collect_service.afe_connector.get_cloud_storage_info()
        )
        try:
            bucket_name = cloud_storage_info["image_storage_server"][5:-1]
        except KeyError:
            _LOGGER.warning(
                "Failed to get network stats because cloud bucket "
                "is not fetched. Return DEFAULT frequency level."
            )
            return Frequency.DEFAULT

        if not bucket_name:
            _LOGGER.warning(
                "Cloud bucket name is none. Return DEFAULT " "frequency level."
            )
            return Frequency.DEFAULT

        try:
            output_file = "/moblab/network.json"
            run_gcloud_bucket_diagnosis(output_file, bucket_name)

            with open(output_file) as output:
                network_json = json.load(output)
            server_errors = network_json["request_errors"]
            broken_connections = network_json["connection_breaks"]
            upload_bits_per_second = int(
                network_json["write_throughput"]["bytes_per_second"] * 8
            )

        except (RunCommandError, KeyError) as err:
            _LOGGER.warning(
                "Failed to get network status from network "
                "diagonosis and return DEFAULT frequency level: "
                "%s",
                err,
            )
            return Frequency.DEFAULT

        # TODO(chromium:1113365): Abstract the config access into its own class.
        high_threshold = self.config["network_thresholds"][
            "upload_bits_per_second"
        ]["high"]
        median_threshold = self.config["network_thresholds"][
            "upload_bits_per_second"
        ]["medium"]

        if (
            server_errors > 0
            or broken_connections > 0
            or upload_bits_per_second < median_threshold
        ):
            return Frequency.ALERT
        if upload_bits_per_second < high_threshold:
            return Frequency.WARNING
        return Frequency.DEFAULT

    def _get_freq_based_on_memory_stats(self):
        """
            Obtains a scheduler frequency level that suits the current memory
            status.

        Returns:
            A Frequency enum.
        """
        memory_stats = psutil.virtual_memory()
        memory_usage = memory_stats.percent / 100.0

        high_threshold = self.config["memory_usage_thresholds"]["high"]
        median_threshold = self.config["memory_usage_thresholds"]["medium"]

        if memory_usage >= high_threshold:
            return Frequency.ALERT
        if memory_usage >= median_threshold:
            return Frequency.WARNING
        return Frequency.DEFAULT

    def schedule(self):
        """
        Schedules the collection and upload of moblab and duts data
        according to the their respective message types and frequencies.
        """
        job_list = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            # Submits jobs to collect and update Moblab data.
            for attr_type in self.moblab_attr_types:
                job_list.append(
                    executor.submit(
                        self.collect_and_upload, self.MOBLAB, attr_type
                    )
                )

            # Submits jobs to collect and update DUT data.
            for attr_type in self.dut_attr_types:
                job_list.append(
                    executor.submit(
                        self.collect_and_upload, self.DUT, attr_type
                    )
                )

            # Submits jobs to update data collection frequencies based on memory
            # stats and network stats.
            # Memory Stats: check every 10 mins.
            # Network Stats: check every 12 hours.
            job_list.append(
                executor.submit(
                    self.update_freq_level,
                    self._get_freq_based_on_memory_stats,
                    10,
                )
            )
            job_list.append(
                executor.submit(
                    self.update_freq_level,
                    self._get_freq_based_on_network_stats,
                    720,
                )
            )

            # Execute all the submitted jobs.
            for job in as_completed(job_list):
                try:
                    job.result()
                except Exception:
                    _LOGGER.exception("Failed to start the scheduler.")
