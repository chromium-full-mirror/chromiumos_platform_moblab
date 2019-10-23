#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import print_function

import argparse
import re
import sys
import os
import datetime
from dateutil.tz import tzlocal
import time
from concurrent import futures

import grpc

from moblab_common import afe_connector
from moblab_common import config_connector
from moblab_common import devserver_connector
import build_connector
import moblab_rpcservice
# pylint: disable=import-error
import moblabrpc_pb2
# pylint: disable=import-error
import moblabrpc_pb2_grpc
try:
    from chromite.lib import cros_logging as logging
except ImportError:
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

    def run_suite(self, request, _context):
        return moblabrpc_pb2.RunSuiteResponse(
            message='Hello, %s!' % request.name)

    def run_cts_suite(self, request, _context):
        response = moblabrpc_pb2.RunCtsSuiteResponse(
            message=self.service
            .run_cts_suite(request.build_target, request.build, request.suite,
                           request.model, request.pool))
        return response

    def list_connected_duts(self, _request, _context):
        response = moblabrpc_pb2.ListConnectedDutsResponse()
        duts = self.service.list_duts()
        for dut in duts:
            dut_info = moblabrpc_pb2.ConnectedDutInfo(
                name=dut.get('platform', ''),
                ip=dut.get('hostname', ''),
                mac_addr='',
                models=self.service.extract_model_from_labels(
                    dut.get('labels', [])),
                build_targets=self.service.extract_build_target_from_labels(
                    dut.get('labels', [])),
                pools=self.service.extract_pool_from_labels(
                    dut.get('labels', [])),
                status=dut['status'],
                is_enrolled=True,
                labels=dut.get('labels', []),
                attributes=dut.get('attributes', []),
                error=dut.get('error', ''))
            response.duts.extend([dut_info])
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
        response = moblabrpc_pb2.ListBuildsResponse(
            builds=self.build_connector.get_builds_for_milestone(
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
        num_jobs = self.service.get_num_jobs()
        response = moblabrpc_pb2.GetNumJobsResponse(num_jobs=num_jobs)
        return response

    def convert_timestamp_to_utc_secs(self, ts):
        dt_ts = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        dt_ts.replace(tzinfo=tzlocal())
        #TODO(haddowk) converty to UTC timezone
        return int((dt_ts - datetime.datetime(1970, 1, 1)).total_seconds())

    def get_jobs(self, request, _context):
        jobs = self.service.get_jobs()

        response = moblabrpc_pb2.GetJobsResponse()
        if jobs:
            for job in jobs:
                job_proto = moblabrpc_pb2.Job(
                    job_id=job.get('id', -1),
                    name=job.get('name', 'Name not found'),
                    priority=job.get('priority', 0),
                    created_time_sec_utc=self.convert_timestamp_to_utc_secs(
                        job['created_on']),
                    parent_job_id=job.get('parent_job', -1))
                response.jobs.extend([job_proto])
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
