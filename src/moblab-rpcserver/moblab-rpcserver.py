#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import print_function

import re
import os
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
from chromite.lib import cros_logging as logging

model_re = re.compile(r'^model:(.*)')
board_re = re.compile(r'^board:(.*)')
pool_re = re.compile(r'^pool:(.*)')

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS',
                      '%s/.service_account.json' % os.environ['HOME'])


class MoblabRpcService(moblabrpc_pb2_grpc.MoblabRpcServiceServicer):

    def __init__(self):
        super(MoblabRpcService, self).__init__()
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector)
        self.service = moblab_rpcservice.MoblabLogic()
        self.setup_devserver_connector()

    def setup_devserver_connector(self):
        self.moblab_bucket_name = self.config_connector.get_cloud_bucket()
        logging.info('Using bucket: %s', self.moblab_bucket_name)
        self.devserver_connector = devserver_connector.DevserverConnector(
            self.moblab_bucket_name)
        try:
            self.build_connector = build_connector.MoblabBuildConnector(
                self.moblab_bucket_name)
        except build_connector.MoblabBuildConnectorException as e:
            logging.info(e)
            self.build_connector = None

    def run_suite(self, request, _context):
        return moblabrpc_pb2.RunSuiteResponse(
            message='Hello, %s!' % request.name)

    def run_cts_suite(self, request, _context):
        response = moblabrpc_pb2.RunCtsSuiteResponse(
            message=self.service
            .run_cts_suite(request.board, request.build, request.suite, request
                           .model, request.pool))
        return response

    def list_connected_duts(self, _request, _context):
        afe_hosts = self.afe_connector.get_connected_devices()
        potential_hosts = self.service.get_connected_devices()
        response = moblabrpc_pb2.ListConnectedDutsResponse()
        dut_infos = []
        for host in afe_hosts:
            dut = moblabrpc_pb2.ConnectedDutInfo(
                name=host['platform'],
                ip=host['hostname'],
                mac_addr='',
                models=self.service.extract_model_from_labels(
                    host.get('labels', [])),
                boards=self.service.extract_board_from_labels(
                    host.get('labels', [])),
                pools=self.service.extract_pool_from_labels(
                    host.get('labels', [])),
                status=host['status'],
                is_enrolled=True,
                labels=host.get('labels', []),
                attributes=host.get('attributes', []))
            dut_infos.append(dut)
        for host in potential_hosts:
            dut = moblabrpc_pb2.ConnectedDutInfo(
                name=host['platform'],
                ip=host['hostname'],
                mac_addr='',
                models=[],
                boards=[],
                pools=[],
                status='Not enrolled',
                is_enrolled=False,
                labels=[],
                attributes=[])
        dut_infos.append(dut)
        response.duts.extend(dut_infos)
        return response

    def list_test_jobs(self, request, context):
        pass

    def list_boards(self, _request, _context):
        response = moblabrpc_pb2.ListBoardsResponse(
            boards=self.build_connector.get_boards_available())
        return response

    def list_milestones(self, request, _context):
        response = moblabrpc_pb2.ListMilestonesResponse(
            milestones=self.build_connector.get_milestones_available(request
                                                                     .board))
        return response

    def list_builds(self, request, _context):
        response = moblabrpc_pb2.ListBuildsResponse(
            builds=self.build_connector.get_builds_for_milestone(
                request.board, request.milestone))
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


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=500))

    try:
        moblabrpc_pb2_grpc.add_MoblabRpcServiceServicer_to_server(
            MoblabRpcService(), server)
        server.add_insecure_port('[::]:6002')
        server.start()
        while True:
            time.sleep(60 * 60 * 24)
    except build_connector.MoblabBuildConnectorException:
        pass
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
