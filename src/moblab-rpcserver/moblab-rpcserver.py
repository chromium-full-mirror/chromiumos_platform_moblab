#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import argparse
import calendar
import datetime
import grpc
import os
import re
import sys
import time

from concurrent import futures
from dateutil.tz import tzlocal

import moblab_rpcservice
# pylint: disable=import-error
import moblabrpc_pb2
# pylint: disable=import-error
import moblabrpc_pb2_grpc

from moblab_common import afe_connector
from moblab_common import build_connector
from moblab_common import config_connector
from moblab_common import devserver_connector
from moblab_common import feedback_connector

import logging

model_re = re.compile(r'^model:(.*)')
pool_re = re.compile(r'^pool:(.*)')

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS',
                      '%s/.service_account.json' % os.environ['HOME'])


class MoblabRpcService(moblabrpc_pb2_grpc.MoblabRpcServiceServicer):

    def __init__(self):
        super(MoblabRpcService, self).__init__()
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector)
        self.service = moblab_rpcservice.MoblabService()
        self.setup_devserver_connector()
        self.has_credentials = True

    def setup_devserver_connector(self):
        self.moblab_bucket_name = self.config_connector.get_cloud_bucket()
        logging.info('Using bucket: %s', self.moblab_bucket_name)
        self.devserver_connector = devserver_connector.DevserverConnector(
            self.moblab_bucket_name)
        try:
            self.build_connector = build_connector.MoblabBuildConnector(
                self.moblab_bucket_name)
        except build_connector.MoblabBuildConnectorException as e:
            self.build_connector = None
            logging.info('Setting has_credentials to false')
            self.has_credentials = False

    def send_moblab_screenshot(self, request, _context):
        """Uploads image and feedback text to GCS.

        Args:
          request: SendMoblabRequest object with a string description and a
            Base64 serialized png image screenshot.
          _context: grpc.server.Context

        Returns:
          SendMoblabResponse type with string message indicating location of
          uploaded feedback.
        """
        fc = feedback_connector.MoblabFeedbackConnector(self.moblab_bucket_name)
        path, url = fc.upload_feedback(request.description, request.screenshot)
        response = moblabrpc_pb2.SendMoblabScreenshotResponse(
            message='Feedback uploaded to bucket {} under {}. URL to screenshot: {}'.format(self.moblab_bucket_name, path, url)
        )
        return response

    def run_suite(self, request, _context):
        """Generic run suite method. Accepts suite as a custom argument, allows
        for run of any suite but with no custom arguments.

        Args:
          request: RunSuiteRequest object with parameters describing suite to be
          run and arguments for suite run.
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
          request: RunCtsSuiteRequest object with parameters describing suite to be
          run and arguments for suite run:
            build_target: Ex. octopus
            milestone: Ex. R80
            build_version: A numeric version string of the form: '00000.00.0'
            android_version: A string specifying which android version suite to
             run ( Ex. cts_X )
            model: String identfier for the specific model to be run.
            pool: String identifier for which pool of DUT's to run tests with.
            specific_modules: Comma-separated string of specific module names to
            run.
          _context: grpc.server.Context
        Returns:
          RunSuiteResponse object with a string result message.
        """
        response = moblabrpc_pb2.RunSuiteResponse(
            message=self.service
            .run_cts_suite(
                request.build_target,
                request.model,
                request.milestone,
                request.build_version,
                request.android_version,
                request.pool,
                request.specific_modules
            ))
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
                specific_modules: Comma-separated string of specific module names to
                run.
              _context: grpc.server.Context
            Returns:
              RunSuiteResponse object with a string result message.
            """
        response = moblabrpc_pb2.RunSuiteResponse(
            message=self.service
                .run_gts_suite(
                request.build_target,
                request.model,
                request.milestone,
                request.build_version,
                request.pool,
                request.specific_modules
            ))
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
          _context: grpc.server.Context
        Returns:
          RunSuiteResponse object with a string result message.
        """
        response = moblabrpc_pb2.RunSuiteResponse(
            message = self.service.run_storage_qual_suite(
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
            message = self.service.run_memory_qual_suite(
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

    def get_connected_dut_from_dict(self, dut_dict):
        return moblabrpc_pb2.ConnectedDutInfo(
            name=dut_dict.get('platform', ''),
            ip=dut_dict.get('hostname', ''),
            mac_addr='',
            models=self.service.extract_model_from_labels(
                dut_dict.get('labels', [])),
            build_targets=self.service.extract_build_target_from_labels(
                dut_dict.get('labels', [])),
            pools=self.service.extract_pool_from_labels(
                dut_dict.get('labels', [])),
            status=dut_dict['status'],
            is_enrolled=True,
            is_connected=dut_dict.get('isConnected', True),
            labels=dut_dict.get('labels', []),
            attributes=dut_dict.get('attributes', []),
            error=dut_dict.get('error', '')
        )

    def list_connected_duts(self, _request, _context):
        response = moblabrpc_pb2.ListConnectedDutsResponse()
        duts = self.service.list_duts()
        for dut in duts:
            dut_info = self.get_connected_dut_from_dict(dut)
            response.duts.extend([dut_info])
        return response

    def get_dut_details(self, request, _context):
        try:
            dut = self.service.get_dut_details(request.dut)[0]
        except IndexError:
            error_msg = 'Unable to find DUT: {}'.format(request.dut)
            logging.error(error_msg)
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details(error_msg)
        else:
            response = moblabrpc_pb2.GetDutDetailsResponse(
                dut_detail=self.get_connected_dut_from_dict(dut)
            )
            if 'current_job' in dut:
                response.dut_detail.current_job = dut['current_job'] if dut['current_job'] else 0
            if 'current_special_task' in dut:
                response.dut_detail.current_dut_task =\
                    dut['current_special_task'] if dut['current_special_task'] else ''
        return response

    def list_test_jobs(self, request, context):
        pass

    def list_build_targets(self, _request, _context):
        build_targets = self.service.list_usable_build_targets()
        response = moblabrpc_pb2.ListBuildTargetsResponse(
            build_targets=build_targets)
        return response

    def list_milestones(self, request, _context):
        response = moblabrpc_pb2.ListMilestonesResponse(
            milestones=self.build_connector.get_milestones_available(
                request.build_target))
        return response

    def list_build_versions(self, request, _context):
        response = moblabrpc_pb2.ListBuildVersionsResponse(
            build_versions=self.build_connector.get_builds_for_milestone(
                request.build_target, request.milestone))
        return response

    def list_pools(self, _request, _context):
        afe_hosts = self.afe_connector.get_connected_devices()
        pools = []
        for host in afe_hosts:
            pools.extend(
                self.service.extract_pool_from_labels(host.get('labels', [])))
        response = moblabrpc_pb2.ListPoolsResponse(pools=pools)
        return response

    def list_models(self, _request, _context):
        afe_hosts = self.afe_connector.get_connected_devices()
        models = []
        for host in afe_hosts:
            models.extend(
                self.service.extract_model_from_labels(host.get('labels', [])))
        response = moblabrpc_pb2.ListModelsResponse(models=models)
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
        logging.info('Firmware list requested')
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
        self.service.update_duts_firmware(request.ips)
        response = moblabrpc_pb2.UpdateDutsFirmwareResponse()
        return response

    def get_num_jobs(self, request, _context):
        num_jobs = self.service.get_num_jobs(
            request.id_filter, request.name_filter, request.created_time_lt,
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
            dt_ts = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
            to_utc_delta_seconds = calendar.timegm(
                time.gmtime()) - calendar.timegm(time.localtime())
            return int((dt_ts - datetime.datetime(1970, 1, 1)).total_seconds()) + \
                   to_utc_delta_seconds
        except (ValueError, TypeError) as e:
            logging.error('Encountered an invalid string for conversion to' +
                          ' timestamp: {}'.format(ts))
            return None

    def _extract_status_enum(self, status_str):
        if status_str == 'Queued':
            return moblabrpc_pb2.Job.QUEUED
        elif status_str == 'Provisioned':
            return moblabrpc_pb2.Job.PROVISIONED
        elif status_str == 'Running':
            return moblabrpc_pb2.Job.RUNNING
        elif status_str == 'Completed':
            return moblabrpc_pb2.Job.SUCCESS
        elif status_str == 'Failed':
            return moblabrpc_pb2.Job.FAILED
        elif status_str == 'Aborted':
            return moblabrpc_pb2.Job.ABORTED
        else:
            logging.error(
                'Encountered unexpected status "{}"'.format(status_str))
            return moblabrpc_pb2.Job.STATUS_NOT_SET

    def _extract_status(self, job):
        if job.get('status'):
            return self._extract_status_enum(job.get('status'))
        elif job.get('status_counts'):
            # "if there is more than one status count, error out"
            if len(job.get('status_counts').keys()) != 1 or \
                job.get('status_counts')[list(job.get('status_counts').keys())[0]] != 1:
                logging.error(
                    'Encountered multiple status values for job {}'.format(job))
                return moblabrpc_pb2.Job.STATUS_NOT_SET
            return self._extract_status_enum(list(job.get('status_counts').keys())[0])
        else:
            logging.error('Unable to find status for job {}'.format(job))
            return moblabrpc_pb2.Job.STATUS_NOT_SET

    def get_jobs(self, request, _context):
        jobs = self.service.get_jobs(
            request.query_start, request.query_limit, request.id_filter,
            request.name_filter, request.created_time_lt,
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
                    job_id=job.get('id', -1),
                    name=job.get('name', 'Name not found'),
                    priority=job.get('priority', 0),
                    created_time_sec_utc=self._convert_timestamp_to_utc_secs(
                        job['created_on']),
                    parent_job_id=job.get('parent_job', -1),
                    status=self._extract_status(job))
                response.jobs.extend([job_proto])
        return response

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
        response = moblabrpc_pb2.GetJobIdsResponse(
            job_ids = job_ids
        )
        return response

    def abort_jobs(self, request, _context):
        message = self.service.abort_jobs(
            # converting proto RepeatedScalarFieldContainer type to python list
            [job_id for job_id in request.job_ids]
        )
        response =  moblabrpc_pb2.AbortJobsResponse()
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
            logging.error('Got invalid timedelta values {} {}'.format(
                minutes, seconds))
            return None

    def get_job_details(self, request, _context):
        try:
            job = self.service.get_job_details(request.id)[0]
        except IndexError:
            error_msg = 'Unable to find job with ID: {}'.format(request.id)
            logging.error(error_msg)
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            _context.set_details(error_msg)
        else:
            execution_history = [
                moblabrpc_pb2.Execution(
                    name=item.get('name', ''),
                    job_id=item.get('id', ''),
                    status=self._extract_status(item),
                    start_time_utc=self._convert_timestamp_to_utc_secs(
                        item.get('start_time', '')),
                    end_time_utc=self._convert_timestamp_to_utc_secs(
                        item.get('end_time', '')),
                    used_time=self._convert_timedelta_to_miliseconds(
                        seconds=item.get('time_used', '')),
                    dut=item.get('hostname', ''))
                for item in self.service.get_job_history(request.id)
            ]

            associated_duts = []
            for item in self.service.get_associated_duts(request.id):
                try:
                    dut = item['host']['hostname']
                except (KeyError, TypeError):
                    dut = 'unknown'

                try:
                    dut_status = item['host']['status']
                except (KeyError, TypeError):
                    dut_status = ''

                status = self._extract_status(item)
                associated_duts.append(moblabrpc_pb2.Execution(
                        dut=dut,
                        dut_status=dut_status,
                        status=status
                    )
                )

            response = moblabrpc_pb2.GetJobDetailsResponse(
                job_detail=moblabrpc_pb2.Job(
                    job_id=job.get('id'),
                    name=job.get('name', ''),
                    priority=job.get('priority', 0),
                    created_time_sec_utc=self._convert_timestamp_to_utc_secs(
                        job.get('created_on', '')),
                    parent_job_id=job.get('parent_job', None),
                    status=self._extract_status(job),
                    dependencies=job.get('dependencies', ''),
                    server_control_file=job.get('control_file', ''),
                    max_runtime=self._convert_timedelta_to_miliseconds(
                        minutes=job.get('max_runtime_mins', '')),
                    timeout=self._convert_timedelta_to_miliseconds(
                        minutes=job.get('timeout_mins', '')),
                    test_retries=job.get('test_retry', None),
                    execution_history=execution_history,
                    associated_duts=associated_duts
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
        return moblabrpc_pb2.GetNumDutTasksResponse(num_dut_tasks=num_dut_tasks)

    def _extract_dut_task_status(self, dut_task_dict):
        """
            Given a dict representing a dut_task, will extract a status enum
            based on the provided boolean flags.
        """
        try:
            if dut_task_dict['is_aborted']:
                return moblabrpc_pb2.DutTask.ABORTED
            elif dut_task_dict['success']:
                return moblabrpc_pb2.DutTask.SUCCEEDED
            elif dut_task_dict['is_complete']:
                return moblabrpc_pb2.DutTask.FAILED
            elif dut_task_dict['is_active']:
                return moblabrpc_pb2.DutTask.STARTED
            else:
                return moblabrpc_pb2.DutTask.REQUESTED
        except KeyError:
            logging.error('Failed to determine dut task status for:\n{}'
                          .format(dut_task_dict))
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
            request.end_time_lt
        )

        if dut_task_list is None:
            _context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        response = moblabrpc_pb2.GetDutTasksResponse()
        for dut_task_dict in dut_task_list:
            dut_task = moblabrpc_pb2.DutTask(
                id=dut_task_dict.get('id', ''),
                task=dut_task_dict.get('task', ''),
                status=self._extract_dut_task_status(
                    dut_task_dict),
                created_time_utc=self._convert_timestamp_to_utc_secs(
                    dut_task_dict.get('time_requested', '')),
                started_time_utc=self._convert_timestamp_to_utc_secs(
                    dut_task_dict.get('time_started', '')),
                finished_time_utc=self._convert_timestamp_to_utc_secs(
                    dut_task_dict.get('time_finished', '')),
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
            request.dut_hostnames,
            request.key,
            request.value
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
        response =  moblabrpc_pb2.ReverifyHostResponse(
            message=message
        )
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
        response =  moblabrpc_pb2.RepairHostResponse(
            message=message
        )
        return response


def setup_logging(level):
    """Enable the correct level of logging.

    Args:
        level (int): One of the predefined logging levels, e.g loging.DEBUG
    """
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(level)
    fh = logging.FileHandler('/var/log/moblab/moblab_rpc.log')
    fh.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)


def parse_arguments(argv):
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Turn on debug logging.')
    return parser.parse_args(argv)


def serve():
    options = parse_arguments(sys.argv[1:])
    logging_severity = logging.INFO
    if options.verbose:
        logging_severity = logging.DEBUG
    setup_logging(logging_severity)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=500))

    moblab_service = MoblabRpcService()

    try:
        moblabrpc_pb2_grpc.add_MoblabRpcServiceServicer_to_server(
            moblab_service, server)

        server.add_insecure_port('[::]:6002')
        logging.info('Starting server')
        server.start()
        while True:
            logging.info('Server sleepin')
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
