# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import grpc
import moblabrpc_pb2
import moblabrpc_pb2_grpc


def list_connected_duts(stub):
    request = moblabrpc_pb2.ListConnectedDutsRequest()
    print((stub.list_connected_duts(request)))


def get_num_jobs(stub):
    request = moblabrpc_pb2.GetNumJobsRequest()
    print((stub.get_num_jobs(request)))


def get_jobs(stub):
    request = moblabrpc_pb2.GetNumJobsRequest()
    print((stub.get_jobs(request)))


if __name__ == '__main__':
    channel = grpc.insecure_channel('localhost:6002')
    stub = moblabrpc_pb2_grpc.MoblabRpcServiceStub(channel)
    get_jobs(stub)
