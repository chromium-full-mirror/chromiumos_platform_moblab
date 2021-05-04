# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import distutils
import docker
import google.api_core
import os
import re
import requests
import subprocess
import time
import logging

from collections import namedtuple
from datetime import datetime
from google.cloud import storage

from moblab_common import build_connector
from moblab_common import dut_connector
from moblab_common import host_connector
from moblab_common import moblab_build_connector

from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common import result_upload_status_connector

from host_scheduler_pause_service import HostSchedulerPauseService

MilestonePair = namedtuple("MilestonePair", ["milestone", "is_staged"])
BuildVersionPair = namedtuple(
    "BuildVersionPair", ["build_version", "status", "is_staged"]
)
BuildResults = namedtuple("BuildResults", ["results", "is_incomplete"])

_DEFAULT_SUITE_TIMEOUT_MINS = 1440
_SUITE_TIMEOUT_MAP = {
    "hardware_storagequal": 40320,
    "hardware_storagequal_quick": 40320,
    "storage_qual_v2_xs": 720,  # 12 hours
    "storage_qual_v2_s": 2880,  # 2 days
    "storage_qual_v2_m": 5760,  # 4 days
    "storage_qual_v2_l": 14400,  # 10 days
    "storage_qual_v2_xl": 28800,  # 20 days
    "cts": 2880,  # 2 days
    "gts": 2880,  # 2 days
}

_STORAGE_QUAL_VARIATIONS = {
    0: "hardware_storagequal",
    1: "hardware_storagequal_quick",
    2: "hardware_storagequal_external",
    3: "storage_qual_v2_quick",
    4: "storage_qual_v2_xs",
    5: "storage_qual_v2_s",
    6: "storage_qual_v2_m",
    7: "storage_qual_v2_l",
    8: "storage_qual_v2_xl",
}

HARDWARE_AVL_BUG_ID = "bug_id"
HARDWARE_AVL_PART_NO = "part_id"

STORAGE_QUAL_DISK_SIZE_GB = "tast_disk_size_gb"
STORAGE_QUAL_DUAL_NAMESPACE = "tast_storage_slc_qual"

MOBLAB_DOCKER_REGISTRY = "gcr.io/chromeos-partner-moblab/"

MAX_BUILD_STAGING_SECONDS = 300  # 5 minutes


class MoblabRpcError(Exception):
    pass


class MoblabService(object):
    model_re = re.compile(r"^model:(.*)")
    build_target_re = re.compile(r"^board:(.*)")
    pool_re = re.compile(r"^pool:(.*)")

    _last_config_update = None
    _last_build_connector_update = None
    _last_moblab_build_connector_update = None

    def __init__(self):
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector
        )
        self.setup_devserver_connector()
        self.dut_connector = dut_connector.MoblabDUTConnector()
        self.pause_service = HostSchedulerPauseService()
        self.upload_status_connector = (
            result_upload_status_connector.ResultUploadStatusConnector()
        )

    def _find_dut_id_given_ip(self, dut_hostname):
        """Given an ip address, will return the id given to the DUT by AFE.
        Raises:
             MoblabRpcError: if unable to find the DUT.
        """
        try:
            return self.afe_connector.get_connected_devices(
                hostname=dut_hostname
            )[0]["id"]
        except (IndexError, KeyError):
            msg = "Unable to find AFE id for dut: {}".format(dut_hostname)
            logging.error(msg)
            raise MoblabRpcError(msg)

    def setup_devserver_connector(self):
        self.moblab_bucket_name = self.config_connector.get_cloud_bucket()
        logging.info("Using bucket: %s", self.moblab_bucket_name)
        self._init_build_connector(raise_error=False)

    def _init_build_connector(self, raise_error=True):
        try:
            self._build_connector = build_connector.MoblabBuildConnector(
                self.moblab_bucket_name
            )
        except build_connector.MoblabBuildConnectorException:
            logging.exception("Failed to initialize MoblabBuildConnector.")
            if raise_error:
                raise

    def _init_moblab_build_connector(self, raise_error=True):
        """
        Creates a MoblabBuildConnector for Moblab API calls to get build items.
        Args:
            raise_error: if true, will raise any exception encountered during
            init attempt.
        Returns:
          MoblabBuildConnector.
        """
        try:
            self._moblab_build_connector = (
                moblab_build_connector.MoblabBuildConnector()
            )
        except build_connector.MoblabBuildConnectorException:
            logging.exception("Failed to initialize MoblabBuildConnector.")
            if raise_error:
                raise

    @property
    def build_connector(self):
        """
        Returns a build_connector.MoblabBuildConnector instance ( distinct from
        moblab_build_connector.MoblabBuildConnector ),

        TODO(wangmichael) change naming so that difference between two
        connectors is more clear.
        """
        if (
            not hasattr(self, "_build_connector")
            or not self._build_connector
            or self._last_config_update != self._last_build_connector_update
        ):
            self.moblab_bucket_name = self.config_connector.get_cloud_bucket(
                force_reload=True
            )
            self._init_build_connector()
            self._last_build_connector_update = self._last_config_update
        return self._build_connector

    @property
    def moblab_build_connector(self):
        """
        Returns a moblab.build_connector.MoblabBuildConnector instance
        ( distinct from build_connector.MoblabBuildConnector ),
        """
        if (
            not hasattr(self, "_moblab_build_connector")
            or not self._moblab_build_connector
            or self._last_config_update
            != self._last_moblab_build_connector_update
        ):
            self.moblab_bucket_name = self.config_connector.get_cloud_bucket(
                force_reload=True
            )
            self._init_moblab_build_connector()
            self._last_moblab_build_connector_update = self._last_config_update

        return self._moblab_build_connector

    def _is_moblab_bucket_in_asia(self):
        if not self.moblab_bucket_name:
            raise MoblabRpcError(
                (
                    "Attempted to check bucket location while bucket has not"
                    " been configured."
                )
            )

        bucket = storage.Client().bucket(self.moblab_bucket_name)
        bucket.reload()
        return "asia" in bucket.location.lower()

    def extract_model_from_labels(self, labels):
        try:
            return self.extract_from_labels(self.model_re, labels)[0]
        except IndexError:
            logging.exception("Failed to parse model from label tags of DUT.")
            return ""

    def extract_build_target_from_labels(self, labels):
        try:
            return self.extract_from_labels(self.build_target_re, labels)[0]
        except IndexError:
            logging.exception(
                "Failed to parse build target from label tags of DUT."
            )
            return ""

    def extract_pool_from_labels(self, labels):
        return self.extract_from_labels(self.pool_re, labels)

    def extract_from_labels(self, regexp, labels):
        result = [
            m.group(1) for m in [regexp.match(label) for label in labels] if m
        ]
        return list(set(result))

    def get_connected_devices(self):
        connected_duts = self.dut_connector.get_connected_duts()
        afe_formatted_duts = []
        for dut in connected_duts:
            afe_formatted_duts.append(
                {"ip": dut[0], "isConnected": dut[1], "error": dut[2]}
            )
        return afe_formatted_duts

    def list_duts(self):
        """Returns the merge of enrolled and connected DUTs"""
        afe_hosts = self.afe_connector.get_connected_devices()
        potential_hosts = self.get_connected_devices()
        connected_ips = []
        connected_duts = []

        for dut in afe_hosts:
            dut["enrolled"] = True
            connected_ips.append(dut["hostname"])
            connected_duts.append(dut)

        for dut in potential_hosts:
            if dut["ip"] not in connected_ips:
                dut["hostname"] = dut["ip"]
                dut["enrolled"] = False
                dut["status"] = "Not Enrolled"
                dut["error"] = dut["error"]
                connected_duts.append(dut)

        self._hydrate_dut_details_with_mac(connected_duts)

        return connected_duts

    def _default_suite_timeout_mins(self, suite):
        if suite in _SUITE_TIMEOUT_MAP:
            return _SUITE_TIMEOUT_MAP[suite]
        else:
            return _DEFAULT_SUITE_TIMEOUT_MINS

    def run_storage_qual_suite(
        self,
        build_target,
        model,
        milestone,
        build_version,
        bug_id,
        part_id,
        variation,
        pool=None,
        disk_size_gb=0,
        is_dual_namespace=False,
    ):
        """Starts storage qual suite run. Formats arguments s.t. they can be
        ingested by AFE.

        Args:
            build_target: Ex. octopus
            model: String identifier for the specific model to be run.
            milestone: String, Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            bug_id: Numeric string identifying the associated
            buganizer issue.
            part_id: Numeric string identifying relevant part number.
            variation: RunStorageQualificationSuiteRequest.Variation
            pool: String identifier for which pool of DUT's to run tests with.
            disk_size_gb: Size of main storage disk (in whole GB).
            is_dual_namespace: Dual-namespace test requested.
        Returns:
          String response message.
        """
        avl_args = {
            HARDWARE_AVL_BUG_ID: bug_id,
            HARDWARE_AVL_PART_NO: part_id,
            STORAGE_QUAL_DISK_SIZE_GB: disk_size_gb,
            STORAGE_QUAL_DUAL_NAMESPACE: is_dual_namespace,
        }

        return self.run_suite(
            build_target,
            model,
            milestone,
            build_version,
            _STORAGE_QUAL_VARIATIONS[variation],
            pool,
            suite_args=avl_args,
            test_args=avl_args,
        )

    def run_memory_qual_suite(
        self,
        build_target,
        model,
        milestone,
        build_version,
        bug_id,
        part_id,
        pool=None,
    ):
        """Starts memory qual suite run. Formats arguments s.t. they can be
        ingested by AFE.

        Args:
            build_target: Ex. octopus
            model: String identifer for the specific model to be run.
            milestone: String,  Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            bug_id: Numeric string identifying the associated buganizer issue.
            part_id: Numeric string identifying relevant part number.
            pool: String identifier for which pool of DUT's to run tests with.
        Returns:
          String response message.
        """
        avl_args = {HARDWARE_AVL_BUG_ID: bug_id, HARDWARE_AVL_PART_NO: part_id}
        return self.run_suite(
            build_target,
            model,
            milestone,
            build_version,
            "hardware_memoryqual",  # suite
            pool,
            suite_args=avl_args,
            test_args=avl_args,
        )

    def run_cts_suite(
        self,
        build_target,
        model,
        milestone,
        build_version,
        suite,
        pool=None,
        autotest_tests=None,
    ):
        """Starts cts suite run. Formats arguments s.t. they can be ingested by
        AFE.

        Args:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            specific_modules: List of strings of specific module names to
            run.
        Returns:
          String response message.
        """

        suite_args = {}
        if autotest_tests and len(autotest_tests):
            suite_args["tests"] = [test.strip() for test in autotest_tests]

        return self.run_suite(
            build_target,
            model,
            milestone,
            build_version,
            suite,
            pool,
            suite_args=suite_args,
        )

    def run_gts_suite(
        self,
        build_target,
        model,
        milestone,
        build_version,
        pool=None,
        autotest_tests=None,
    ):
        """Starts gts suite run. Formats arguments s.t. they can be ingested by
        AFE.

        Args:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identifer for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            specific_modules: Comma-separated string of specific module names
            to run.
        Returns:
          String response message.
        """
        suite_args = {}
        if autotest_tests:
            suite_args["tests"] = [test.strip() for test in autotest_tests]

        return self.run_suite(
            build_target,
            model,
            milestone,
            build_version,
            "gts",  # suite
            pool,
            suite_args=suite_args,
        )

    def run_suite_faft(
        self,
        build_target,
        build_version,
        suite,
        model=None,
        pool=None,
        ro_firmware=None,
        rw_firmware=None,
    ):
        build_versions = {}
        if rw_firmware:
            build_versions["fwrw-version"] = rw_firmware
        if ro_firmware:
            build_versions["fwro-version"] = ro_firmware

    def run_suite(
        self,
        build_target,
        model,
        milestone,
        build_version,
        suite,
        pool=None,
        suite_args={},
        test_args={},
        suite_timeout_mins=None,
        extra_builds={},
    ):
        """Starts suite run. Formats input arguments s.t. that they can be used
        by an AFE suite run command.

        Args:
            build_target: Ex. octopus
            milestone: Numeric string Ex. 80
            build_version: A numeric version string of the form: '00000.00.0'
            suite: String identifier for the suite to be run.
            model: String identifer for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            suite_args: Dict containing key=val pairs to be used by suite
              control file.
            test_args: Dict containing key=val pairs to be used by test control
              file.
        Returns:
          String response message.
        """

        if not self._is_build_staged(
            build_version, build_target, milestone, model
        ):
            self._stage_build(model, build_target, build_version)

        build = "{}-release/R{}-{}".format(
            build_target, milestone, build_version
        )
        builds = {"cros-version": build}

        builds.update(extra_builds)

        if not suite_timeout_mins:
            suite_timeout_mins = self._default_suite_timeout_mins(suite)

        dut_wifi_info = self.get_dut_wifi_info()
        ap_name=dut_wifi_info.get("wifi_dut_ap_name", None)
        ap_pass=dut_wifi_info.get("wifi_dut_ap_pass", "")

        test_args["ssid"] = ap_name
        test_args["wifipass"] = ap_pass

        suite_job_id, error = self.afe_connector.run_suite(
            build_target,
            build,
            builds,
            suite,
            suite_timeout_mins,
            pool,
            model,
            suite_args=suite_args,
            test_args=test_args,
        )

        if not suite_job_id:
            raise MoblabRpcError("Encountered error starting suite")

        return "Suite started (suite job ID: {})".format(suite_job_id)

    def provision_duts(self, pool, milestone, build_version):
        ModelBoard = namedtuple("ModelBoard", ["model", "board"])

        boards = {}
        duts = self.list_duts()
        for dut in duts:
            labels = dut.get("labels", [])
            pools = self.extract_pool_from_labels(labels)

            if pool and pool not in pools:
                continue

            model = self.extract_model_from_labels(labels)
            board = self.extract_build_target_from_labels(labels)
            modelBoardPair = ModelBoard(model=model, board=board)
            if modelBoardPair in boards:
                boards[modelBoardPair] += 1
            else:
                boards[modelBoardPair] = 1

        messages = []
        for modelBoardPair, number in boards.items():
            try:
                self.run_suite(
                    modelBoardPair.board,
                    modelBoardPair.model,
                    milestone,
                    build_version,
                    "provision",
                    pool=pool,
                    suite_args={"num_required": number},
                )
            except MoblabRpcError as ex:
                messages.append(str(ex))
        return ", ".join(messages)

    def enroll_duts(self, ip_addresses):
        self.afe_connector.enroll_duts(ip_addresses)
        self.pause_service.ensure_duts_pause_state(list(ip_addresses))

    def unenroll_duts(self, ip_addresses):
        self.afe_connector.unenroll_duts(ip_addresses)

    def list_connected_duts_firmware(self):
        duts = self.dut_connector.get_connected_dut_firmware()
        return duts

    def get_dut_details(self, dut):
        dut_details = self.afe_connector.get_connected_devices(
            dut, get_current_jobs=True
        )
        self._hydrate_dut_details_with_mac(dut_details)
        return dut_details

    def _hydrate_dut_details_with_mac(self, duts_details):
        dut_ip_to_mac_map = {
            ip: mac
            for (
                ip,
                mac,
            ) in self.dut_connector.get_all_known_mac_addresses().items()
        }
        for dut in duts_details:
            if dut["hostname"] in dut_ip_to_mac_map:
                dut["mac"] = dut_ip_to_mac_map[dut["hostname"]]

    def update_duts_firmware(self, ip_addresses):
        return self.dut_connector.update_firmware(ip_addresses)

    def _is_build_staged(self, build_version, build_target, milestone, model):
        """
            Checks if targeted build is staged. Defaults to checking staging
            status via Moblab API, falls back to checking the configured GCS
            bucket directly.
        Args:
            build_target (string): AKA board of the target DUT.
            build_version (string): Build version to be applied to DUT for
                testing.
            milestone (string): Milestone the build version belongs to.
            model (string): Model of the DUT.
        Returns:
            Boolean which is true iff build is already staged on Moblab.
        """
        try:
            return self.moblab_build_connector.check_build_stage_status(
                build_target, model, build_version, self.moblab_bucket_name
            )
        except google.api_core.exceptions.GoogleAPIError:
            logging.exception(
                (
                    "Encountered API error while checking build stage status "
                    "for {}/{} on model {}"
                ).format(build_target, build_version, model)
            )
            return (
                build_version
                in self.build_connector.get_builds_for_milestone(
                    build_target, milestone
                )
            )

    def _stage_build(self, model, build_target, build_version):
        """
            Applies the specified build artifacts to the bucket configured
            for this Moblab.

        Args:
            model (string): Model of the target DUT.
            build_target (string): AKA board of the target DUT.
            build_version (string): Build version to be applied to DUT for
                testing.
        Returns:
            Nothing.
        """
        self.moblab_build_connector.stage_build(
            build_target, model, build_version, self.moblab_bucket_name
        )

        sleep_interval = 1
        end_time = time.time() + MAX_BUILD_STAGING_SECONDS
        while time.time() < end_time:
            if self.moblab_build_connector.check_build_stage_status(
                build_target, model, build_version, self.moblab_bucket_name
            ):
                return
            time.sleep(sleep_interval)
            # every failure, increase wait interval by 1.5 times
            # ( exponential backoff, of sorts )
            sleep_interval *= 1.5
        raise MoblabRpcError(
            "Build stage did not finish within {} seconds.".format(
                MAX_BUILD_STAGING_SECONDS
            )
        )

    def list_usable_build_targets(self, model):
        """
            Returns build targets associated with the given model.
        Args:
            mode(str): DUT model to return associated build_target(s) for.
        Returns:
            List of build target strings.
        """
        afe_hosts = self.afe_connector.get_connected_devices()
        build_targets = set()
        for host in afe_hosts:
            if self.extract_model_from_labels(host.get("labels", [])) == model:
                build_targets.add(
                    self.extract_build_target_from_labels(
                        host.get("labels", [])
                    )
                )
        return list(build_targets)

    def list_usable_milestones(self, build_target, model):
        """
        Returns milestones available for a given model/build_target, both
        staged and unstaged (if target bucket is in US, otherwise will only
        return staged milestones).

        In this context, 'remote' means unstaged/from API call (i.e., remote
        milestones are those that are fetched from the Moblab API rather than
        from existing build items staged in the partner bucket ).

        Args:
            build_target(string): build_target (AKA board) to fetch milestones
              for.
            model(string): model to fetch milestones for.
        Returns:
            A list of tuples where the first item is the milestone and the
            second is a boolean which is true iff at least one build of the
            milestone is staged.
        """
        bucket_milestones = self.build_connector.get_milestones_available(
            build_target
        )

        remote_milestones = []
        if not self._is_moblab_bucket_in_asia():
            try:
                remote_milestones = (
                    self.moblab_build_connector.list_available_milestones(
                        build_target,
                        model,
                    )
                )
            except moblab_build_connector.MoblabBuildConnectorException:
                logging.exception(
                    "Encountered error trying to fetch remote milestones."
                )

        milestone_results = [
            MilestonePair(milestone=milestone, is_staged=True)
            for milestone in bucket_milestones
        ]
        milestone_results.extend(
            [
                MilestonePair(milestone=milestone, is_staged=False)
                for milestone in list(
                    set(remote_milestones).difference(set(bucket_milestones))
                )
            ]
        )

        milestone_results.sort(
            key=lambda x: int(x[0].strip("R")), reverse=True
        )
        return BuildResults(
            results=milestone_results,
            is_incomplete=(
                len(remote_milestones)
                == moblab_build_connector.DEFAULT_PAGE_SIZE
            ),
        )

    def list_usable_build_versions(self, build_target, milestone, model):
        """
        Returns build versions available for a given
        model/build_target/milestone, both staged and unstaged (if target
        bucket is in US, otherwise will only return staged build versions).

        In this context, 'remote' means unstaged/from API call (i.e., remote
        build versions are those that are fetched from the Moblab API rather
        than from existing build items staged in the partner bucket ).

        Args:
            build_target(string): build_target (AKA board) to return build
                versions for.
            model(string): model to return build versions for.
            milestone(string): milestone to return build versions for.
        Returns:
            A list of tuples where the first item is the build_version and the
            second is a boolean which is true iff the build is staged.
        """
        bucket_build_versions = self.build_connector.get_builds_for_milestone(
            build_target, milestone
        )

        build_version_results = [
            BuildVersionPair(
                build_version=build_version,
                status="pass",
                is_staged=True
            )
            for build_version in bucket_build_versions
        ]

        remote_build_versions = []
        if not self._is_moblab_bucket_in_asia():
            try:
                remote_build_versions = (
                    self.moblab_build_connector.list_builds_for_milestone(
                        build_target, model, milestone
                    )
                )
            except moblab_build_connector.MoblabBuildConnectorException:
                logging.exception(
                    "Encountered error trying to fetch remote build versions."
                )

        staged_builds_set = set(bucket_build_versions)
        for build_version in remote_build_versions:
            if build_version.version not in staged_builds_set:
                build_version_results.append(
                    BuildVersionPair(
                        build_version=build_version.version,
                        status=build_version.status,
                        is_staged=False
                    )
                )

        build_version_results.sort(
            key=lambda x: distutils.version.LooseVersion(x[0]), reverse=True
        )
        return BuildResults(
            results=build_version_results,
            is_incomplete=(
                len(remote_build_versions)
                == moblab_build_connector.DEFAULT_PAGE_SIZE
            ),
        )

    def get_num_jobs(
        self,
        id_filter=None,
        name_filter=None,
        created_time_lt=None,
        created_time_gt=None,
        sub=False,
        suite=False,
        not_yet_run=False,
        running=False,
        finished=False,
        parent_id_filter=None,
        dut_hostname_filter=None,
    ):
        # TO_DO(wangmichael): bifurcating on dut_filter is necessary because
        # the Autotest backend that we currently invoke only accepts dut_filter
        # on calls to get_num_host_queue_entries, not get_num_jobs. Even
        # though, in both cases, the results are packaged and returned as jobs.
        # This may change when Autotest RPC itself is refactored.
        if dut_hostname_filter:
            try:
                dut_id = self.afe_connector.get_connected_devices(
                    hostname=dut_hostname_filter
                )[0]["id"]
            except (IndexError, KeyError):
                logging.error(
                    "Unable to find AFE id for dut: {}".format(
                        dut_hostname_filter
                    )
                )
                return
            return self.afe_connector.get_num_host_queue_entries(
                host_id=dut_id
            )
        else:
            return self.afe_connector.get_num_jobs(
                id_filter,
                name_filter,
                created_time_lt,
                created_time_gt,
                sub,
                suite,
                not_yet_run,
                running,
                finished,
                parent_id_filter,
            )

    def get_jobs(
        self,
        query_start,
        query_limit,
        id_filter=None,
        name_filter=None,
        created_time_lt=None,
        created_time_gt=None,
        sub=False,
        suite=False,
        not_yet_run=False,
        running=False,
        finished=False,
        parent_id_filter=None,
        dut_hostname_filter=None,
    ):
        # TO_DO(wangmichael): bifurcating on dut_filter is necessary because
        # the Autotest backend that we currently invoke only accepts dut_filter
        # on calls to get_host_queue_entries, not get_jobs. Even though,
        # in both cases, the results are packaged and returned as jobs. This
        # may change when Autotest RPC itself is refactored.
        jobs = []

        if dut_hostname_filter:
            try:
                dut_id = self.afe_connector.get_connected_devices(
                    hostname=dut_hostname_filter
                )[0]["id"]
            except (IndexError, KeyError):
                logging.error(
                    "Unable to find AFE id for dut: {}".format(
                        dut_hostname_filter
                    )
                )
                return
            hqes, _ = self.afe_connector.get_host_queue_entries(
                host_id=dut_id,
                query_start=query_start,
                query_limit=query_limit,
            )

            # Extracting jobs information from HQE entries.
            for hqe in hqes:
                job = hqe["job"]
                job["status"] = hqe.get("status")
                jobs.append(job)

        else:
            jobs = self.afe_connector.get_jobs(
                query_start,
                query_limit,
                id_filter,
                name_filter,
                created_time_lt,
                created_time_gt,
                sub,
                suite,
                not_yet_run,
                running,
                finished,
                parent_id_filter,
            )
        job_ids = [job["id"] for job in jobs]

        jobs_upload_status = (
            self.upload_status_connector.get_jobs_upload_status(job_ids)
        )
        for job in jobs:
            if job["id"] in jobs_upload_status:
                state = jobs_upload_status[job["id"]]
                job["upload_status"] = state.status
                job["attempt_number"] = state.attempt_number
                job["last_falure_reason"] = state.last_falure_reason

        return jobs

    def get_job_ids(
        self,
        query_start,
        query_limit,
        id_filter=None,
        name_filter=None,
        created_time_lt=None,
        created_time_gt=None,
        sub=False,
        suite=False,
        not_yet_run=False,
        running=False,
        finished=False,
        parent_id_filter=None,
        dut_hostname_filter=None,
    ):
        """Returns the job ID's that match the request filters.

        Args:
            query_start: Int index for start of returned values.
            query_limit: Int for max number of values to return.
            id_filter: String filter for job id.
            name_filter: String filter for job name.
            created_time_lt: A unix timestamp in seconds granularity the sets
                upper bound for jobs returned.
            created_time_gt: A unix timestamp in seconds granularity the sets
                lower bound for jobs returned.
            sub: Boolean, true iff child jobs to be returned.
            suite: Boolean, true iff parent jobs to be returned.
            not_yet_run: Boolean, true iff queued jobs to be returned.
            running: Boolean, true iff running jobs to be returned.
            finished: Boolean, true iff only finished jobs to be returned.
            parent_id_filter: String filter for parent job id.
            dut_hostname_filter: String filter for DUT associated with job.

        Returns:
          List of job ID numbers.
        """
        return [
            job["id"]
            for job in self.get_jobs(
                query_start,
                query_limit,
                id_filter,
                name_filter,
                created_time_lt,
                created_time_gt,
                sub,
                suite,
                not_yet_run,
                running,
                finished,
                parent_id_filter,
                dut_hostname_filter,
            )
        ]

    def abort_jobs(self, job_ids):
        result = self.afe_connector.abort_host_queue_entries(job_ids)
        if result:
            aborted_jobs = [str(item["Job"]) for item in result]
            if len(aborted_jobs) > 15:
                return (
                    "Aborted {} jobs, please refresh table" " to see results."
                ).format(len(aborted_jobs))
            else:
                return (
                    "Aborted the following jobs: {}\nPlease refresh "
                    "table to see results."
                ).format(", ".join(aborted_jobs))
        else:
            return (
                "No jobs aborted (were selected jobs already "
                "aborted/finished)?"
            )

    def get_job_details(self, job_id):
        return self.afe_connector.get_jobs_by_ids([job_id])

    def get_job_history(self, job_id):
        return self.afe_connector.get_job_history(job_id)

    def get_associated_duts(self, job_id):
        hqes, _ = self.afe_connector.get_host_queue_entries(job_id=job_id)
        return hqes

    def get_num_dut_tasks(self, ip, start_time_gt, end_time_lt):
        """
            Given a DUT's IP, returns a number of tasks (e.g. repairs,
            reverifies) associated with that DUT.
        Args:
            ip (string): DUT IP.
            start_time_gt(int): Seconds timestamp of a filter to DUT tasks by
                start time.
            end_time_lt(int): Seconds timestamp of a filter to DUT tasks by
                end time.
        Returns:
            Returns number of task associated with DUT which match query
            parameters.  If DUT itself is not found, returns -1.
        """
        try:
            dut_id = self.afe_connector.get_connected_devices(hostname=ip)[0][
                "id"
            ]
            return self.afe_connector.get_num_special_tasks(
                host_id_list=[dut_id],
                start_time_gt=start_time_gt,
                end_time_lt=end_time_lt,
            )
        except (IndexError, KeyError):
            logging.error("Unable to find AFE id for dut: {}".format(dut_id))
            return -1

    def get_dut_tasks(
        self, ip, query_start, query_limit, start_time_gt, end_time_lt
    ):
        """
            Given a DUT's IP, returns a list of tasks (e.g. repairs,
            reverifies) requested for that DUT. If DUT is not found, returns
            None.
        Args:
            query_start(int): Parameter specifying index on where to start when
                returning paged results.
            query_limit(int): Upper limit on number of results to return.
            start_time_gt(int): Seconds timestamp of a filter to DUT tasks by
                start time.
            end_time_lt(int): Seconds timestamp of a filter to DUT tasks by
                end time.
        Returns:
            A list of dicts, each dict specifying a task associated with the
            queried DUT. If DUT is not found returns None.
        """
        try:
            dut_id = self.afe_connector.get_connected_devices(hostname=ip)[0][
                "id"
            ]
            return self.afe_connector.get_special_tasks(
                host_id_list=[dut_id],
                query_start=query_start,
                query_limit=query_limit,
                start_time_gt=start_time_gt,
                end_time_lt=end_time_lt,
            )
        except (IndexError, KeyError):
            logging.error("Unable to find AFE id for dut: {}".format(dut_id))

    def add_label_to_host(self, dut_hostname, label):
        return self.afe_connector.add_label_to_host(dut_hostname, label)

    def remove_label_from_host(self, dut_hostname, label):
        return self.afe_connector.remove_label_to_host(dut_hostname, label)

    def _apply_edit_to_duts(
        self, dut_hostnames, afe_edit_func, success_msg, *args
    ):
        """
            A helper function which contains the repeated logic involved in
            applying an edit to multiple DUTs. This logic is repeated for
            adding and removing attributes and labels.
        Args:
            dut_hostnames(string[]): A list of strings representing the
                hostnames of the DUT's to be targeted.
            afe_edit_func((*args) => (tuple(bool,string))): A reference to a
                function of AFEConnector which takes in *args and returns a
                tuple containing a bool indicating success and a results
                message string. This function does the 'edit' to the DUT's.
            success_msg(int): A format-able string to be returned in success
                cases; It should have exactly as many format indexes ({}) as
                there are arguments in *args.
            *args: Arguments which are meant to be passed into afe_edit_func.
        Returns:
            String message summarizing results.
        """
        failures = {}
        for dut_hostname in dut_hostnames:
            is_success, message = afe_edit_func(dut_hostname, *args)
            if not is_success:
                failures[dut_hostname] = message

        response_message = success_msg.format(*args) + " to {} DUTs\n".format(
            len(dut_hostnames) - len(failures.keys())
        )

        if failures:
            response_message += "Failures on the following DUTs:\n"
            for dut_hostname, message in failures.items():
                response_message += "{}: {}\n".format(dut_hostname, message)

        return response_message

    def add_attribute_to_duts(self, dut_hostnames, key, value):
        """
            Adds attribute key:value to the selected dut_hostnames. Returns a
            message summarizing how many DUT's the attribute was successfully
            added to as well for which DUT's the addition failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the
              hostnames
            of the DUT's to be targeted.
            key (string): Key of attribute to be added.
            value (string): Value of attribute to be added.
        Returns:
            String message summarizing results.
        """
        return self._apply_edit_to_duts(
            dut_hostnames,
            # self.add_attribute_to_host,
            self.afe_connector.add_attribute_to_host,
            "Successfully added attribute {}:{}",
            key,
            value,
        )

    def remove_attribute_from_duts(self, dut_hostnames, key):
        """
            Removes attribute (referenced by key) from the selected
            dut_hostnames. Returns a message summarizing how many DUT's the
            attribute was successfully removed from as well for which DUT's the
            remove failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the
                hostnames of the DUT's to be targeted.
            key (string): Key of attribute to be remove.
            value (string): Value of attribute to be remove.
        Returns:
            String message summarizing results.
        """
        return self._apply_edit_to_duts(
            dut_hostnames,
            self.afe_connector.remove_attribute_from_host,
            "Successfully removed attribute {}",
            key,
        )

    def add_label_to_duts(self, dut_hostnames, label):
        """
            Adds label to the selected dut_hostnames. Returns a message
            summarizing how many DUT's the label was successfully added to as
            well for which DUT's the addition failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the
                hostnames of the DUT's to be targeted.
            label (string): Label to be added.
        Returns:
            String message summarizing results.
        """
        return self._apply_edit_to_duts(
            dut_hostnames,
            self.afe_connector.add_label_to_host,
            "Successfully added label {}",
            label,
        )

    def remove_label_from_duts(self, dut_hostnames, label):
        """
            Remove label from the selected dut_hostnames. Returns a message
            summarizing how many DUT's the label was successfully removed from
            as well as for which DUT's the remove failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the
                hostnames of the DUT's to be targeted.
            label (string): Label to be removed.
        Returns:
            String message summarizing results.
        """
        return self._apply_edit_to_duts(
            dut_hostnames,
            self.afe_connector.remove_label_from_host,
            "Successfully removed label {}",
            label,
        )

    def add_pool_to_duts(self, dut_hostnames, pool):
        """
            Adds  pool to the selected dut_hostnames. Returns a message
            summarizing how many DUT's the  pool was successfully added to as
            well for which DUT's the addition failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the
                hostnames of the DUT's to be targeted.
            pool (string): Pool to be added.
        Returns:
            String message summarizing results.
        """
        return self.add_label_to_duts(dut_hostnames, "pool:" + pool)

    def remove_pool_from_duts(self, dut_hostnames, pool):
        """
            Remove  pool from the selected dut_hostnames. Returns a message
            summarizing how many DUT's the  pool was successfully removed from
            as well as for which DUT's the remove failed.
        Args:
            dut_hostnames(string[]): A list of strings representing the
                hostnames of the DUT's to be targeted.
             pool (string): Pool to be removed.
        Returns:
            String message summarizing results.
        """
        return self.remove_label_from_duts(dut_hostnames, "pool:" + pool)

    def reverify_host(self, dut_hostnames):
        """Starts repair run on given DUTs hostnames.

        Args:
            dut_hostnames(string[]): A list of strings representing the
                hostnames of the DUT's to be targeted.
        """
        self.afe_connector.reverify_host(dut_hostnames)
        return "Successfully set off reverify on {}".format(dut_hostnames)

    def repair_host(self, dut_hostname):
        """Starts repair run on given DUT hostname.

        Args:
            dut_hostname(string): String hostname (ex. IP address)
        """
        dut_id = self._find_dut_id_given_ip(dut_hostname)
        if dut_id:
            self.afe_connector.repair_host(dut_id)

        return "Successfully set off repair on {}".format(dut_hostname)

    def get_cloud_configuration(self):
        """
            Gets cloud configuration info.
        Returns:
            A dict of cloud configuration info specifically,
            'gs_access_key_id', 'gs_secret_access_key', 'image_storage_server'
        """
        return self.afe_connector.get_cloud_storage_info()

    def get_dut_wifi_info(self):
        """Gets DUT wifi info.
        Returns:
            A dict with dut_wifi_name, dut_wifi_password
        """
        return self.afe_connector.get_dut_wifi_info()

    def set_dut_wifi_info(self, dut_wifi_name, dut_wifi_password):
        """
            Attempts to set DUT wifi on Moblab.
        Args:
            dut_wifi_name (string): Wifi name
            dut_wifi_password (string): Wifi password
        Returns:
            A result message string.
        """
        if self.afe_connector.set_configuration_info(
            dut_wifi_name=dut_wifi_name,
            dut_wifi_password=dut_wifi_password,
        ):
            return "Successfully applied DUT Wifi info changes."
        else:
            return "Failed to apply DUT Wifi info changes."

    def _can_change_cloud_config(self):
        return self.get_num_jobs() == 0

    def _cloud_config_changing(
        self,
        new_is_cloud_enabled,
        new_boto_key_id,
        new_boto_key_secret,
        new_gcs_bucket_url,
    ):
        old_config = self.get_cloud_configuration()
        old_is_cloud_enabled = old_config.get("is_cloud_enabled", False)
        if old_is_cloud_enabled and not new_is_cloud_enabled:
            return False

        old_boto_key_id = old_config.get("gs_access_key_id", "")
        old_boto_key_secret = old_config.get("gs_secret_access_key", "")
        old_gcs_bucket_url = old_config.get("image_storage_server", "")
        if (
            old_boto_key_id != new_boto_key_id
            or old_boto_key_secret != new_boto_key_secret
            or old_gcs_bucket_url != new_gcs_bucket_url
        ):
            return True
        return False

    def set_cloud_configuration(
        self,
        is_cloud_enabled,
        boto_key_id,
        boto_key_secret,
        gcs_bucket_url,
        is_remote_agent_enabled,
        is_remote_command_enabled,
    ):
        """
            Attempts to set configuration values to Moblab.
        Args:
            boto_key_id (string): boto ID string
            boto_key_secret (string): boto secret string
            gcs_bucket_url (string): GCS bucket URL
        Returns:
            A result message string.
        """
        if is_cloud_enabled:
            if (
                not self._can_change_cloud_config()
                and self._cloud_config_changing(
                    is_cloud_enabled,
                    boto_key_id,
                    boto_key_secret,
                    gcs_bucket_url,
                )
            ):
                logging.warn(
                    "Attempt to modify Cloud Config after it was used."
                )

                return (
                    "Cloud configuration changes are not allowed. "
                    "Please powerwash the Moblab to set new configuration."
                )

            is_valid, details = self.afe_connector.validate_cloud_storage_info(
                boto_key_id, boto_key_secret, gcs_bucket_url
            )

            if is_valid:
                if self.afe_connector.set_configuration_info(
                    is_cloud_enabled,
                    boto_key_id,
                    boto_key_secret,
                    gcs_bucket_url,
                ):
                    message = (
                        "Successfully applied cloud configuration values. "
                    )
                    self._last_config_update = datetime.utcnow()
                    self.moblab_bucket_name = (
                        self.config_connector.get_cloud_bucket(
                            force_reload=True
                        )
                    )

                    if self.set_is_remote_agent_enabled(
                        is_remote_agent_enabled
                    ):
                        message += "Remote agent has been {}. ".format(
                            "enabled"
                            if is_remote_agent_enabled
                            else "disabled"
                        )
                    else:
                        message += (
                            "But failed to set remote agent as {}. ".format(
                                "enabled"
                                if is_remote_agent_enabled
                                else "disabled"
                            )
                        )

                    if self.set_is_remote_command_enabled(
                        is_remote_command_enabled
                    ):
                        message += "Remote command has been {}.".format(
                            "enabled"
                            if is_remote_command_enabled
                            else "disabled"
                        )
                    else:
                        message += (
                            "But failed to set remote command as {}.".format(
                                "enabled"
                                if is_remote_command_enabled
                                else "disabled"
                            )
                        )
                    return message
                else:
                    return "Failed to apply cloud configuration changes."
            else:
                return details
        else:
            if self.afe_connector.set_configuration_info(is_cloud_enabled):
                return "Successfully disabled cloud configuration."
            else:
                return "Failed to commit disable cloud change."

    def _get_public_ip_address(self):
        """Gets the public IP address.

        @return: public ip address as string.
        """
        try:
            return host_connector.HostServicesConnector.get_ip()
        except host_connector.HostServicesException:
            logging.exception("Failed to get ip address from host.")
        return "No IP Address"

    def get_network_info(self):
        """
            Gets network info of Moblab.

            TCP socket is used to test the connectivity. If there is no connectivity,
            try to get the public IP with UDP socket.

        Returns:
            A dict of network information ( specifically, a 'server_ip' and
            'is_connected' which is true iff Moblab is connected to internet.
        """
        ip = self._get_public_ip_address()
        if ip is not None:
            logging.info("Established TCP connection with well known server.")
            return {"server_ip": ip, "is_connected": True}
        return {"server_ip": None, "is_connected": False}

    def get_is_update_available(self):
        """
            Check to see if there is a system update or any containers that
            have updated images.

            Scan the running containers, if the watchtower program has pulled
            down a newer image then the container to image reference tag
            is broken.

            Detect these image tag link breaks and assume that means we have
            an update. Looking through update tools and forums, it seems this
            is the way all update tools work.

        Returns:
            True iff there is an update available.
        """

        try:
            response = (
                host_connector.HostServicesConnector.get_system_update_status()
            )
            if response.current_op.find("IDLE") == -1:
                return True
        except host_connector.HostServicesException:
            logging.exception("Get system update status call failed.")

        client = docker.from_env(timeout=300)
        for container in client.containers.list():
            if len(container.image.tags) == 0:
                return True
        return False

    def _update_docker(self):
        """
            Sets off an update of all docker containers, using watchtower

        Returns: String result message.
        """
        client = docker.from_env(timeout=600)

        try:
            container = client.containers.get("update")
            raise MoblabRpcError("Already updating please wait.")
        except docker.errors.NotFound:
            pass

        label = os.environ.get("WATCHTOWER_TAG", "release")
        container = client.containers.run(
            MOBLAB_DOCKER_REGISTRY + "watchtower:%s" % label,
            volumes=["/var/run/docker.sock:/var/run/docker.sock"],
            name="update",
            detach=True,
            command="--run-once --include-restarting",
        )

        try:
            container.wait(timeout=600)
        except requests.exceptions.ReadTimeout:
            logging.exception("Watchtower update raised an exception.")
            container.stop()
        finally:
            container.remove()
        return "Update finished."

    def _update_system(self):
        """
            Initiates system update if it is available.
        Returns:
            An error message.
        """
        try:
            response = (
                host_connector.HostServicesConnector.install_system_update()
            )
            return response.error
        except host_connector.HostServicesException:
            logging.exception("Install system update raised an exception.")
            return "Failed to install update."

    def update_moblab(self):
        """
            Initiates a system update if available,
            otherwise kicks docker images update.

        Returns:
            Update status string.
        """
        return_message = self._update_system()
        # if a message was returned then reboot was not requested
        if return_message:
            return self._update_docker()
        return "Updating system."

    def get_is_remote_agent_enabled(self):
        """
            Check to see if the remote agent is enabled.

        Returns:
            True iff remote agent is enabled.
        """
        return self.config_connector.get_is_remote_agent_enabled()

    def set_is_remote_agent_enabled(self, is_enabled):
        """
            Attempts to set if the remote agent is enabled.

        Args:
            is_enabled (bool): enable the remote agent or not
        Returns:
            True iff the set operation successfully.
        """
        return self.afe_connector.set_is_remote_agent_enabled(is_enabled)

    def get_is_remote_command_enabled(self):
        """
            Check to see if the remote agent is enabled.

        Returns:
            True iff remote agent is enabled.
        """
        return self.config_connector.is_remote_task_scheduler_enabled()

    def set_is_remote_command_enabled(self, is_enabled):
        """
            Attempts to set if the remote command is enabled.

        Args:
            is_enabled (bool): enable the remote command or not
        Returns:
            True iff the set operation successfully.
        """
        return self.afe_connector.set_is_remote_command_enabled(is_enabled)

    def download_service_account(self):
        """Download the service account from the account bucket.

        To avoid users having to enter two different credentials, they enter
        the boto key and secret, then we download the API key from a known
        file in their bucket.

        This function downloads that file, as it is getting the API key we
        have to use gsutil vs cloud storage API to download.

        """
        self.moblab_bucket_name = self.config_connector.get_cloud_bucket()
        logging.info("Using bucket: %s", self.moblab_bucket_name)
        if not self.moblab_bucket_name:
            raise MoblabRpcError(
                "Need bucket name to copy service account from."
            )
        try:
            subprocess.check_call(
                [
                    "gsutil",
                    "cp",
                    "gs://%s/%s"
                    % (
                        self.moblab_bucket_name,
                        "pubsub-key-do-not-delete.json",
                    ),
                    "/home/moblab/.service_account.json",
                ],
            )

        except subprocess.CalledProcessError:
            logging.exception(
                "Failed to get the service account from %s",
                self.moblab_bucket_name,
            )
            raise MoblabRpcError(
                "Failed to get the service account from %s"
                % self.moblab_bucket_name,
            )
