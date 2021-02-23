#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import calendar
import datetime
import grpc
import logging
import re
import time

# pylint: disable=import-error
import moblab_service

from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common import devserver_connector
from moblab_common import feedback_connector
from moblab_common import host_connector
from moblab_common import moblab_info

# pylint: disable=import-error
from moblab_common.proto import moblabrpc_pb2

# pylint: disable=import-error
from moblab_common.proto import moblabrpc_pb2_grpc

# pylint: disable=import-error
from moblab_common.utils.constants import Constants as MoblabConstants
from moblab_common.result_upload_status_connector import Status as UploadStatus

from google.protobuf import empty_pb2

AFE_TO_MOBLAB_STATUS_MAPPINGS = {
    "Queued": moblabrpc_pb2.Job.QUEUED,
    "Provisioning": moblabrpc_pb2.Job.PROVISIONING,
    "Running": moblabrpc_pb2.Job.RUNNING,
    "Completed": moblabrpc_pb2.Job.SUCCESS,
    "Failed": moblabrpc_pb2.Job.FAILED,
    "Aborted": moblabrpc_pb2.Job.ABORTED,
    "Starting": moblabrpc_pb2.Job.STARTING,
    "Pending": moblabrpc_pb2.Job.PENDING,
    "Resetting": moblabrpc_pb2.Job.RESETTING,
    "Verifying": moblabrpc_pb2.Job.VERIFYING,
    "Gathering": moblabrpc_pb2.Job.GATHERING,
    "Parsing": moblabrpc_pb2.Job.PARSING,
    "Stopped": moblabrpc_pb2.Job.STOPPED,
    "Cleaning": moblabrpc_pb2.Job.CLEANING,
    "Template": moblabrpc_pb2.Job.TEMPLATE,
}


class MoblabRpcService(moblabrpc_pb2_grpc.MoblabRpcServiceServicer):
    def __init__(self):
        super(MoblabRpcService, self).__init__()
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector
        )
        self.service = moblab_service.MoblabService()
        self.setup_devserver_connector()

    def setup_devserver_connector(self):
        self.moblab_bucket_name = self.config_connector.get_cloud_bucket()
        logging.info("Using bucket: %s", self.moblab_bucket_name)
        self.devserver_connector = devserver_connector.DevserverConnector(
            self.moblab_bucket_name
        )

    def send_moblab_screenshot(self, request, _context):
        """Uploads image and feedback text to GCS.

        Args:
          request: SendMoblabRequest object with a string email, string
          description and a Base64 serialized png image screenshot.
          _context: grpc.server.Context

        Returns:
          SendMoblabResponse type with string message indicating location of
          uploaded feedback.
        """
        fc = feedback_connector.MoblabFeedbackConnector(
            self.moblab_bucket_name
        )
        path, url = fc.upload_feedback(
            request.contact_email,
            request.description,
            request.screenshot,
        )
        response = moblabrpc_pb2.SendMoblabScreenshotResponse(
            message=(
                "Feedback uploaded to bucket {} under {}. "
                "URL to screenshot: {}"
            ).format(self.moblab_bucket_name, path, url)
        )
        return response

    def run_suite(self, request, _context):
        """Generic run suite method.

        Accepts suite as a custom argument, allows for run of any suite but
        with no custom arguments.

        Args:
          request: RunSuiteRequest object with parameters describing suite to
          be run and arguments for suite run.
          _context: grpc.server.Context
        Returns:
          RunSuiteResponse object with a string result message.
        """
        return moblabrpc_pb2.RunSuiteResponse(
            message=self.service.run_suite(
                request.build_target,
                request.model,
                request.milestone,
                request.build_version,
                request.suite,
                pool=request.pool,
            )
        )

    def run_cts_suite(self, request, _context):
        """Sets off CTS suite run.

        Args:
          request: RunCtsSuiteRequest object with parameters describing suite
            to be
          run and arguments for suite run:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            android_version: A string specifying which android version suite to
             run ( Ex. cts_X )
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            specific_modules: Comma-separated string of specific module names
            to run.
          _context: grpc.server.Context
        Returns:
          RunSuiteResponse object with a string result message.
        """
        response = moblabrpc_pb2.RunSuiteResponse(
            message=self.service.run_cts_suite(
                request.build_target,
                request.model,
                request.milestone,
                request.build_version,
                request.android_version,
                request.pool,
                request.specific_modules,
            )
        )
        return response

    def run_gts_suite(self, request, _context):
        """Sets off GTS suite run.

        Args:
          request: RunGtsSuiteRequest object with parameters describing
          arguments for suite run:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            specific_modules: Comma-separated string of specific module names
            to run.
          _context: grpc.server.Context
        Returns:
          RunSuiteResponse object with a string result message.
        """
        response = moblabrpc_pb2.RunSuiteResponse(
            message=self.service.run_gts_suite(
                request.build_target,
                request.model,
                request.milestone,
                request.build_version,
                request.pool,
                request.specific_modules,
            )
        )
        return response

    def run_storage_qualification_suite(self, request, _context):
        """Sets off hardware storage qualification suite run.

        Args:
          request: RunStorageQualificationSuiteRequest object with parameters
          describing arguments for suite run:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identifier for the specific model to be run.
            avl_process_bug_id: Numeric string identifying the associated
            buganizer issue.
            avl_part_number: Numeric string identifying relevant part number.
            variation: RunStorageQualificationSuiteRequest.Variation
            disk_size_gb: Size of main storage disk (in whole GB).
            is_dual_namespace: Dual-namespace test requested.
          _context: grpc.server.Context
        Returns:
          RunSuiteResponse object with a string result message.
        """
        response = moblabrpc_pb2.RunSuiteResponse(
            message=self.service.run_storage_qual_suite(
                request.build_target,
                request.model,
                request.milestone,
                request.build_version,
                request.avl_process_bug_id,
                request.avl_part_number,
                request.variation,
                request.pool,
                request.disk_size_gb,
                request.is_dual_namespace,
            )
        )
        return response

    def run_memory_qualification_suite(self, request, _context):
        """Sets off hardware memory qualification suite run.

        Args:
          request: RunMemoryQualificationSuiteRequest object with parameters
          describing arguments for suite run:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            model: String identifier for the specific model to be run.
            avl_process_bug_id: Numeric string identifying the associated
            buganizer issue.
            avl_part_number: Numeric string identifying relevant part number.
          _context: grpc.server.Context
        Returns:
          RunSuiteResponse object with a string result message.
        """
        response = moblabrpc_pb2.RunSuiteResponse(
            message=self.service.run_memory_qual_suite(
                request.build_target,
                request.model,
                request.milestone,
                request.build_version,
                request.avl_process_bug_id,
                request.avl_part_number,
                request.pool,
            )
        )
        return response

    def _get_connected_dut_from_dict(self, dut_dict):
        return moblabrpc_pb2.ConnectedDutInfo(
            name=dut_dict.get("platform", ""),
            ip=dut_dict.get("hostname", ""),
            mac_addr=dut_dict.get("mac", ""),
            model=self.service.extract_model_from_labels(
                dut_dict.get("labels", [])
            ),
            build_target=self.service.extract_build_target_from_labels(
                dut_dict.get("labels", [])
            ),
            pools=self.service.extract_pool_from_labels(
                dut_dict.get("labels", [])
            ),
            status=dut_dict["status"],
            is_enrolled=dut_dict.get("enrolled", False),
            is_connected=dut_dict.get("isConnected", True),
            labels=dut_dict.get("labels", []),
            attributes=[
                "%s: %s" % (key, value)
                for key, value in dut_dict.get("attributes", {}).items()
            ],
            error=dut_dict.get("error", ""),
        )

    def list_connected_duts(self, _request, _context):
        response = moblabrpc_pb2.ListConnectedDutsResponse()
        duts = self.service.list_duts()
        for dut in duts:
            dut_info = self._get_connected_dut_from_dict(dut)
            response.duts.extend([dut_info])
        return response

    def get_dut_details(self, request, _context):
        try:
            dut = self.service.get_dut_details(request.dut)[0]
        except IndexError:
            error_msg = "Unable to find DUT: {}".format(request.dut)
            logging.error(error_msg)
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details(error_msg)
        else:
            response = moblabrpc_pb2.GetDutDetailsResponse(
                dut_detail=self._get_connected_dut_from_dict(dut)
            )
            if "current_job" in dut:
                response.dut_detail.current_job = (
                    dut["current_job"] if dut["current_job"] else 0
                )
            if "current_special_task" in dut:
                response.dut_detail.current_dut_task = (
                    dut["current_special_task"]
                    if dut["current_special_task"]
                    else ""
                )
        return response

    def list_test_jobs(self, request, context):
        pass

    def list_build_targets(self, request, _context):
        """
            Returns build targets associated with the given model.
        Args:
            request: ListBuildTargetsRequest object with model parameter.
            _context: grpc.server.Context
        Returns:
            ListBuildTargetsResponse
        """
        build_targets = self.service.list_usable_build_targets(request.model)
        response = moblabrpc_pb2.ListBuildTargetsResponse(
            build_targets=build_targets
        )
        return response

    def list_milestones(self, request, _context):
        milestones = self.service.list_usable_milestones(
            request.build_target, request.model
        )
        response = moblabrpc_pb2.ListMilestonesResponse(
            milestones=[
                moblabrpc_pb2.BuildItem(
                    value=i.milestone, is_staged=i.is_staged
                )
                for i in milestones.results
            ],
            is_incomplete=milestones.is_incomplete,
        )
        return response

    def list_build_versions(self, request, _context):
        build_versions = self.service.list_usable_build_versions(
            request.build_target, request.milestone, request.model
        )

        response = moblabrpc_pb2.ListBuildVersionsResponse(
            build_versions=[
                moblabrpc_pb2.BuildItem(
                    value=i.build_version, is_staged=i.is_staged
                )
                for i in build_versions.results
            ],
            is_incomplete=build_versions.is_incomplete,
        )
        return response

    def list_pools(self, _request, _context):
        afe_hosts = self.afe_connector.get_connected_devices()
        pools = set()
        for host in afe_hosts:
            pools = pools.union(
                self.service.extract_pool_from_labels(host.get("labels", []))
            )
        response = moblabrpc_pb2.ListPoolsResponse(pools=list(pools))
        return response

    def list_models(self, _request, _context):
        afe_hosts = self.afe_connector.get_connected_devices()
        models = set()
        for host in afe_hosts:
            models.add(
                self.service.extract_model_from_labels(host.get("labels", []))
            )
        response = moblabrpc_pb2.ListModelsResponse(models=list(models))
        return response

    def enroll_duts(self, request, _context):
        self.service.enroll_duts(request.ips)
        response = moblabrpc_pb2.EnrollDutsResponse()
        return response

    def unenroll_duts(self, request, _context):
        self.service.unenroll_duts(request.ips)
        response = moblabrpc_pb2.EnrollDutsResponse()
        return response

    def list_connected_duts_firmware(self, _request, _context):
        logging.info("Firmware list requested")
        duts = self.service.list_connected_duts_firmware()
        response = moblabrpc_pb2.ListConnectedDutsFirmwareResponse()
        for dut in duts:
            dut_firmware_info = moblabrpc_pb2.ConnectedDutFirmwareInfo(
                ip=dut[0],
                current_firmware=dut[1],
                update_firmware=dut[2],
            )
            response.duts.extend([dut_firmware_info])
        return response

    def update_duts_firmware(self, request, _context):
        results = self.service.update_duts_firmware(request.ips)
        response = moblabrpc_pb2.UpdateDutsFirmwareResponse()
        for result in results:
            command_output = moblabrpc_pb2.FirmwareUpdateCommandOutput(
                ip=result[0], command_output=result[1]
            )
            response.outputs.extend([command_output])

        return response

    def get_num_jobs(self, request, _context):
        num_jobs = self.service.get_num_jobs(
            request.id_filter,
            request.name_filter,
            request.created_time_lt,
            request.created_time_gt,
            request.rel_filter == moblabrpc_pb2.Job.CHILD,
            request.rel_filter == moblabrpc_pb2.Job.SUITE,
            request.status_filter == moblabrpc_pb2.Job.QUEUED_JOBS,
            request.status_filter == moblabrpc_pb2.Job.JOBS_RUNNING,
            request.status_filter == moblabrpc_pb2.Job.FINISHED_JOBS,
            request.parent_id_filter,
            request.dut_hostname_filter,
        )
        response = moblabrpc_pb2.GetNumJobsResponse(num_jobs=num_jobs)
        return response

    def _convert_timestamp_to_utc_secs(self, ts):
        if not ts:
            return None
        try:
            dt_ts = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            to_utc_delta_seconds = calendar.timegm(
                time.gmtime()
            ) - calendar.timegm(time.localtime())
            return (
                int((dt_ts - datetime.datetime(1970, 1, 1)).total_seconds())
                + to_utc_delta_seconds
            )
        except (ValueError, TypeError):
            logging.exception(
                "Encountered an invalid string for conversion to"
                + " timestamp: {}".format(ts)
            )
            return None

    def _extract_status_enum(self, status_str):
        if status_str in AFE_TO_MOBLAB_STATUS_MAPPINGS:
            return AFE_TO_MOBLAB_STATUS_MAPPINGS[status_str]
        elif re.match(r"Aborted \(\s*\w+\s*\)", status_str):
            # Ex. Aborted (Running)
            return moblabrpc_pb2.Job.ABORTING
        else:
            logging.error(
                'Encountered unexpected status "{}"'.format(status_str)
            )
            return moblabrpc_pb2.Job.STATUS_NOT_SET

    def _extract_status(self, job):
        if job.get("status"):
            return self._extract_status_enum(job.get("status"))
        elif job.get("status_counts"):
            # "if there is more than one status count, error out"
            if (
                len(job.get("status_counts").keys()) != 1
                or job.get("status_counts")[
                    list(job.get("status_counts").keys())[0]
                ]
                != 1
            ):
                logging.error(
                    "Encountered multiple status values for job {}".format(job)
                )
                return moblabrpc_pb2.Job.STATUS_NOT_SET
            return self._extract_status_enum(
                list(job.get("status_counts").keys())[0]
            )
        else:
            logging.error("Unable to find status for job {}".format(job))
            return moblabrpc_pb2.Job.STATUS_NOT_SET

    def get_jobs(self, request, _context):
        jobs = self.service.get_jobs(
            request.query_start,
            request.query_limit,
            request.id_filter,
            request.name_filter,
            request.created_time_lt,
            request.created_time_gt,
            request.rel_filter == moblabrpc_pb2.Job.CHILD,
            request.rel_filter == moblabrpc_pb2.Job.SUITE,
            request.status_filter == moblabrpc_pb2.Job.QUEUED_JOBS,
            request.status_filter == moblabrpc_pb2.Job.JOBS_RUNNING,
            request.status_filter == moblabrpc_pb2.Job.FINISHED_JOBS,
            request.parent_id_filter,
            request.dut_hostname_filter,
        )

        response = moblabrpc_pb2.GetJobsResponse()
        if jobs:
            for job in jobs:
                job_proto = moblabrpc_pb2.Job(
                    job_id=job.get("id", -1),
                    name=job.get("name", "Name not found"),
                    priority=job.get("priority", 0),
                    created_time_sec_utc=self._convert_timestamp_to_utc_secs(
                        job["created_on"]
                    ),
                    parent_job_id=job.get("parent_job", -1),
                    status=self._extract_status(job),
                    upload_state=moblabrpc_pb2.Job.UploadState(
                        status=self._map_upload_status(
                            job.get("upload_status", "")
                        ),
                        attempts_number=job.get("attempt_number", 0),
                        last_error=job.get("last_falure_reason", None),
                    ),
                )
                response.jobs.extend([job_proto])
        return response

    def _map_upload_status(self, internal_status):
        result = moblabrpc_pb2.Job.UploadStatus.UPLOAD_STATUS_UNKNOWN
        if internal_status == UploadStatus.NOT_READY.name:
            result = moblabrpc_pb2.Job.UploadStatus.UPLOAD_STATUS_NOT_READY
        if internal_status == UploadStatus.QUEUED.name:
            result = moblabrpc_pb2.Job.UploadStatus.UPLOAD_STATUS_QUEUED
        if internal_status == UploadStatus.UPLOADING.name:
            result = moblabrpc_pb2.Job.UploadStatus.UPLOAD_STATUS_UPLOADING
        if internal_status == UploadStatus.UPLOADED.name:
            result = moblabrpc_pb2.Job.UploadStatus.UPLOAD_STATUS_UPLOADED
        if internal_status == UploadStatus.UPLOAD_FAILED.name:
            result = moblabrpc_pb2.Job.UploadStatus.UPLOAD_STATUS_UPLOAD_FAILED
        if internal_status == UploadStatus.DELETED.name:
            result = moblabrpc_pb2.Job.UploadStatus.UPLOAD_STATUS_DELETED

        return moblabrpc_pb2.Job.UploadStatus.Name(result)

    def get_job_ids(self, request, _context):
        """Returns the job ID's that match the request filters.

        Args:
          request: GetJobIdsRequest
          _context:

        Returns:
          GetJobIdsResponse object with a list of ID numerics.
        """
        job_ids = self.service.get_job_ids(
            request.query_start,
            request.query_limit,
            request.id_filter,
            request.name_filter,
            request.created_time_lt,
            request.created_time_gt,
            request.rel_filter == moblabrpc_pb2.Job.CHILD,
            request.rel_filter == moblabrpc_pb2.Job.SUITE,
            request.status_filter == moblabrpc_pb2.Job.QUEUED_JOBS,
            request.status_filter == moblabrpc_pb2.Job.JOBS_RUNNING,
            request.status_filter == moblabrpc_pb2.Job.FINISHED_JOBS,
            request.parent_id_filter,
            request.dut_hostname_filter,
        )
        response = moblabrpc_pb2.GetJobIdsResponse(job_ids=job_ids)
        return response

    def abort_jobs(self, request, _context):
        message = self.service.abort_jobs(
            # converting proto RepeatedScalarFieldContainer type to python list
            [job_id for job_id in request.job_ids]
        )
        response = moblabrpc_pb2.AbortJobsResponse()
        response.message = message
        return response

    def _convert_timedelta_to_miliseconds(self, minutes=None, seconds=None):
        if not minutes and not seconds:
            return None
        try:
            miliseconds = 0
            if minutes:
                miliseconds += int(minutes) * 60 * 1000
            if seconds:
                miliseconds += int(seconds) * 1000
            return miliseconds
        except ValueError:
            logging.error(
                "Got invalid timedelta values {} {}".format(minutes, seconds)
            )
            return None

    def get_job_details(self, request, _context):
        try:
            job = self.service.get_job_details(request.id)[0]
        except IndexError:
            error_msg = "Unable to find job with ID: {}".format(request.id)
            logging.error(error_msg)
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details(error_msg)
        else:
            execution_history = []
            job_history_dicts = self.service.get_job_history(request.id)
            if job_history_dicts:
                execution_history = [
                    moblabrpc_pb2.Execution(
                        name=item.get("name", ""),
                        job_id=item.get("id", ""),
                        status=self._extract_status(item),
                        start_time_utc=self._convert_timestamp_to_utc_secs(
                            item.get("start_time", "")
                        ),
                        end_time_utc=self._convert_timestamp_to_utc_secs(
                            item.get("end_time", "")
                        ),
                        used_time=self._convert_timedelta_to_miliseconds(
                            seconds=item.get("time_used", "")
                        ),
                        dut=item.get("hostname", ""),
                    )
                    for item in job_history_dicts
                ]

            associated_duts = []
            for item in self.service.get_associated_duts(request.id):
                try:
                    dut = item["host"]["hostname"]
                except (KeyError, TypeError):
                    dut = "hostless"

                try:
                    dut_status = item["host"]["status"]
                except (KeyError, TypeError):
                    dut_status = ""

                job_id = int(item.get("id", ""))

                status = self._extract_status(item)
                associated_duts.append(
                    moblabrpc_pb2.Execution(
                        dut=dut,
                        dut_status=dut_status,
                        job_id=job_id,
                        status=status,
                    )
                )

            response = moblabrpc_pb2.GetJobDetailsResponse(
                job_detail=moblabrpc_pb2.Job(
                    job_id=job.get("id"),
                    name=job.get("name", ""),
                    priority=job.get("priority", 0),
                    created_time_sec_utc=self._convert_timestamp_to_utc_secs(
                        job.get("created_on", "")
                    ),
                    parent_job_id=job.get("parent_job", None),
                    status=self._extract_status(job),
                    dependencies=job.get("dependencies", ""),
                    server_control_file=job.get("control_file", ""),
                    max_runtime=self._convert_timedelta_to_miliseconds(
                        minutes=job.get("max_runtime_mins", "")
                    ),
                    timeout=self._convert_timedelta_to_miliseconds(
                        minutes=job.get("timeout_mins", "")
                    ),
                    test_retries=job.get("test_retry", None),
                    execution_history=execution_history,
                    associated_duts=associated_duts,
                )
            )
        return response

    def get_num_dut_tasks(self, request, _context):
        """
        Given a GetNumDutTasksRequest, returns a GetNumDutTasksResponse obj
        which wraps an int representing the number of tasks that match filter
        parameters of the request.
        """
        num_dut_tasks = self.service.get_num_dut_tasks(
            request.ip,
            request.start_time_gt,
            request.end_time_lt,
        )
        if num_dut_tasks < 0:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            return
        return moblabrpc_pb2.GetNumDutTasksResponse(
            num_dut_tasks=num_dut_tasks
        )

    def _extract_dut_task_status(self, dut_task_dict):
        """
        Given a dict representing a dut_task, will extract a status enum
        based on the provided boolean flags.
        """
        try:
            if dut_task_dict["is_aborted"]:
                return moblabrpc_pb2.DutTask.ABORTED
            elif dut_task_dict["success"]:
                return moblabrpc_pb2.DutTask.SUCCEEDED
            elif dut_task_dict["is_complete"]:
                return moblabrpc_pb2.DutTask.FAILED
            elif dut_task_dict["is_active"]:
                return moblabrpc_pb2.DutTask.STARTED
            else:
                return moblabrpc_pb2.DutTask.REQUESTED
        except KeyError:
            logging.error(
                "Failed to determine dut task status for:\n{}".format(
                    dut_task_dict
                )
            )
            return moblabrpc_pb2.DutTask.STATUS_NOT_SET

    def get_dut_tasks(self, request, _context):
        """
        Given a GetDutTasksRequest, returns a GetDutTasksResponse obj which
        wraps a list of DutTask objects that match the given filter
        parameters.
        """
        dut_task_list = self.service.get_dut_tasks(
            request.ip,
            request.query_start,
            request.query_limit,
            request.start_time_gt,
            request.end_time_lt,
        )

        if dut_task_list is None:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        response = moblabrpc_pb2.GetDutTasksResponse()
        for dut_task_dict in dut_task_list:
            dut_task = moblabrpc_pb2.DutTask(
                id=dut_task_dict.get("id", ""),
                task=dut_task_dict.get("task", ""),
                status=self._extract_dut_task_status(dut_task_dict),
                created_time_utc=self._convert_timestamp_to_utc_secs(
                    dut_task_dict.get("time_requested", "")
                ),
                started_time_utc=self._convert_timestamp_to_utc_secs(
                    dut_task_dict.get("time_started", "")
                ),
                finished_time_utc=self._convert_timestamp_to_utc_secs(
                    dut_task_dict.get("time_finished", "")
                ),
            )
            response.tasks.extend([dut_task])
        return response

    def add_attribute_to_duts(self, request, _context):
        """
        Given a AddAttributeToDutsRequest, returns a
        AddAttributeToDutsResponse obj which wraps a message indicating
        which duts the attribute was successfully added on.

        (A call to ListConnectedDuts will also reflect the change)
        """
        response_msg = self.service.add_attribute_to_duts(
            request.dut_hostnames, request.key, request.value
        )

        response = moblabrpc_pb2.AddAttributeToDutsResponse()
        response.message = response_msg
        return response

    def remove_attribute_from_duts(self, request, _context):
        """
        Given a RemoveAttributeFromDutsRequest, returns a
        RemoveAttributeFromDutsResponse obj which wraps a message indicating
        which duts the attribute was successfully removed from.

        (A call to ListConnectedDuts will also reflect the change)
        """
        response_msg = self.service.remove_attribute_from_duts(
            request.dut_hostnames,
            request.key,
        )

        response = moblabrpc_pb2.RemoveAttributeFromDutsResponse()
        response.message = response_msg
        return response

    def add_label_to_duts(self, request, _context):
        """
        Given a AddLabelToDutsRequest, returns a
        AddLabelToDutsResponse obj which wraps a message indicating
        which duts the label was successfully added on.

        (A call to ListConnectedDuts will also reflect the change)
        """
        response_msg = self.service.add_label_to_duts(
            request.dut_hostnames,
            request.label,
        )

        response = moblabrpc_pb2.AddLabelToDutsResponse()
        response.message = response_msg
        return response

    def remove_label_from_duts(self, request, _context):
        """
        Given a RemoveLabelFromDutsRequest, returns a
        RemoveLabelFromDutsResponse obj which wraps a message indicating
        which duts the label was successfully removed from.

        (A call to ListConnectedDuts will also reflect the change)
        """
        response_msg = self.service.remove_label_from_duts(
            request.dut_hostnames,
            request.label,
        )

        response = moblabrpc_pb2.RemoveLabelFromDutsResponse()
        response.message = response_msg
        return response

    def add_pool_to_duts(self, request, _context):
        """
        Given a AddPoolToDutsRequest, returns a
        AddPoolDutsResponse obj which wraps a message indicating
        which duts the pool was successfully added on.

        (A call to ListConnectedDuts will also reflect the change)
        """
        response_msg = self.service.add_pool_to_duts(
            request.dut_hostnames,
            request.pool,
        )

        response = moblabrpc_pb2.AddPoolToDutsResponse()
        response.message = response_msg
        return response

    def remove_pool_from_duts(self, request, _context):
        """
        Given a RemovePoolFromDutsRequest, returns a
        RemovePoolFromDutsResponse obj which wraps a message indicating
        which duts the pool was successfully removed from.

        (A call to ListConnectedDuts will also reflect the change)
        """
        response_msg = self.service.remove_pool_from_duts(
            request.dut_hostnames,
            request.pool,
        )

        response = moblabrpc_pb2.RemovePoolFromDutsResponse()
        response.message = response_msg
        return response

    def reverify_host(self, request, _context):
        """
            Sets of reverify job on specified DUT.
        Args:
            request: ReverifyHostRequest with parameter:
                dut_hostname(string)
            _context: grpc.server.Context
        Returns:
            ReverifyHostResponse
        """
        message = self.service.reverify_host(request.dut_hostname)
        response = moblabrpc_pb2.ReverifyHostResponse(message=message)
        return response

    def repair_host(self, request, _context):
        """
            Sets of repair job on specified DUT.
        Args:
            request: RepairHostRequest with parameter:
                dut_hostname(string)
            _context: grpc.server.Context
        Returns:
            RepairHostResponse
        """
        message = self.service.repair_host(request.dut_hostname)
        response = moblabrpc_pb2.RepairHostResponse(message=message)
        return response

    def get_network_info(self, request, _context):
        """
            Gets network info of Moblab.
        Args:
            request: GetNetworkInfoRequest object ( with no parameters )
            _context: grpc.server.Context
        Returns:
            GetNetworkInfoResponse
        """
        network_info = moblab_info.get_network_info()
        response = moblabrpc_pb2.GetNetworkInfoResponse(
            moblab_hostname=network_info["server_ip"],
            is_connected=network_info["is_connected"],
        )
        return response

    def get_dut_wifi_info(self, request, _context):
        """
            Gets DUT wifi info configured for Moblab.
        Args:
            request: GetDutWifiInfoRequest object ( with no parameters )
            _context: grpc.server.Context
        Returns:
            GetDutWifiInfoResponse
        """
        dut_wifi_info = self.service.get_dut_wifi_info()
        response = moblabrpc_pb2.GetDutWifiInfoResponse(
            dut_wifi_name=dut_wifi_info.get("wifi_dut_ap_name", ""),
            dut_wifi_password=dut_wifi_info.get("wifi_dut_ap_pass", ""),
        )
        return response

    def set_dut_wifi_info(self, request, _context):
        """
            Set DUT wifi info configured for Moblab.
        Args:
            request: SetDutWifiInfoRequest object with parameters:
                dut_wifi_name,
                dut_wifi_password
            _context: grpc.server.Context
        Returns:
            GetDutWifiInfoResponse
        """
        msg = self.service.set_dut_wifi_info(
            request.dut_wifi_name,
            request.dut_wifi_password,
        )
        response = moblabrpc_pb2.SetDutWifiInfoResponse(message=msg)
        return response

    def get_cloud_configuration(self, request, _context):
        """
            Get cloud configuration info of Moblab.
        Args:
            request: GetCloudConfigurationRequest object ( with no parameters )
            _context: grpc.server.Context
        Returns:
            GetCloudConfigurationResponse
        """
        cloud_configuration = self.service.get_cloud_configuration()
        is_remote_agent_enabled = self.service.get_is_remote_agent_enabled()
        is_remote_command_enabled = (
            self.service.get_is_remote_command_enabled()
        )
        response = moblabrpc_pb2.GetCloudConfigurationResponse(
            is_cloud_enabled=cloud_configuration.get(
                "is_cloud_enabled", "False"
            )
            == "True",
            boto_key_id=cloud_configuration.get("gs_access_key_id", ""),
            boto_key_secret=cloud_configuration.get(
                "gs_secret_access_key", ""
            ),
            gcs_bucket_url=cloud_configuration.get("image_storage_server", ""),
            is_remote_console_enabled=is_remote_agent_enabled,
            is_remote_command_enabled=is_remote_command_enabled,
        )
        return response

    def set_cloud_configuration(self, request, _context):
        """
            Set cloud configuration info of Moblab.
        Args:
            request: SetCloudConfigurationRequest object with parameters:
                is_cloud_enabled,
                boto_key_id,
                boto_key_secret,
                gcs_bucket_url,
                is_remote_console_enabled
            _context: grpc.server.Context
        Returns:
            GetCloudConfigurationResponse
        """
        msg = self.service.set_cloud_configuration(
            request.is_cloud_enabled,
            request.boto_key_id,
            request.boto_key_secret,
            request.gcs_bucket_url,
            request.is_remote_console_enabled,
            request.is_remote_command_enabled,
        )
        response = moblabrpc_pb2.SetCloudConfigurationResponse(message=msg)
        return response

    def get_version_info(self, request, _context):
        """
            Get version info of Moblab.
        Args:
            request: GetVersionInfoRequest object ( with no parameters )
            _context: grpc.server.Context
        Returns:
            GetVersionInfoResponse
        """
        version_info = moblab_info.get_version_info()
        response = moblabrpc_pb2.GetVersionInfoResponse(
            chromeos_release_version=version_info.get(
                MoblabConstants.BUILD_VERSION_NAME, "No Os Version"
            ),
            chromeos_release_track=version_info.get(
                MoblabConstants.CHANNEL_NAME, "No Track Name"
            ),
            chromeos_release_description=version_info.get(
                MoblabConstants.DESCRIPTION_NAME, "No Description"
            ),
            moblab_install_id=version_info.get(
                MoblabConstants.MOBLAB_INSTALL_ID_NAME, "No Install ID"
            ),
            moblab_serial_number=version_info.get(
                MoblabConstants.MOBLAB_HOST_ID_NAME, "No Host ID"
            ),
        )
        return response

    def reboot_moblab(self, request, _context):
        try:
            host_connector.HostServicesConnector.reboot()
        except host_connector.HostServicesException as e:
            return moblabrpc_pb2.RebootMoblabResponse(error_message=str(e))
        return moblabrpc_pb2.RebootMoblabResponse()

    def get_is_update_available(self, request, _context):
        """
            Get whether an update is available for user to pull.
        Args:
            request: GetIsUpdateAvailableRequest object ( with no parameters )
            _context: grpc.server.Context
        Returns:
            GetIsUpdateAvailableResponse ( with a boolean true iff an update is
            available ).
        """
        is_update_available = self.service.get_is_update_available()
        response = moblabrpc_pb2.GetIsUpdateAvailableResponse(
            is_update_available=is_update_available
        )
        return response

    def update_moblab(self, request, _context):
        """
            Set off an update of moblab.
        Args:
            request: UpdateMoblabRequest object ( with no parameters )
            _context: grpc.server.Context
        Returns:
            UpdateMoblabResponse ( with a string result message ).
        """
        message = self.service.update_docker()
        response = moblabrpc_pb2.UpdateMoblabResponse(message=message)
        return response

    def get_remote_agent_configuration(self, request, _context):
        """
            Get remote agent configuration info of Moblab.
        Args:
            request: GetRemoteAgentConfigurationRequest object
                (with no parameters)
            _context: grpc.server.Context
        Returns:
            GetRemoteAgentConfigurationResponse
        """
        return moblabrpc_pb2.GetRemoteAgentConfigurationResponse(
            is_enabled=self.service.get_is_remote_agent_enabled()
        )

    def set_remote_agent_configuration(self, request, _context):
        """
            Set remote agent configuration info of Moblab.
        Args:
            request: SetRemoteAgentConfigurationRequest object with a
                parameter: is_enabled
            _context: grpc.server.Context
        Returns:
            SetRemoteAgentConfigurationResponse
        """
        is_succeeded = self.service.set_is_remote_agent_enabled(
            is_enabled=request.is_enabled
        )
        return moblabrpc_pb2.SetRemoteAgentConfigurationResponse(
            is_succeeded=is_succeeded
        )

    def download_service_account(self, unused_request, unused_context):
        """Copy the service account to local machine.

        The service account is stored in the cloud account bucket, copy it
        to the local drive for use by services.
        """
        self.service.download_service_account()
        return empty_pb2.Empty()
