#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import grpc
import hostservices_pb2
import hostservices_pb2_grpc


def get_host_identifier(st):
    request = hostservices_pb2.HostIdentifierRequest()
    print((st.get_host_identifier(request)))

def is_service_running(st, service):
    request = hostservices_pb2.ServiceRunningRequest()
    request.service = service
    print(st.is_service_running(request))

def get_disk_info(st):
    request = hostservices_pb2.DiskInfoRequest()
    print(st.get_disk_info(request))

def get_ip(st):
    request = hostservices_pb2.GetIpRequest()
    print(st.get_ip(request))

def check_for_system_update(st):
    request = hostservices_pb2.SystemUpdateCheckRequest()
    print(st.check_for_system_update(request))

def get_system_update_status(st):
    request = hostservices_pb2.SystemUpdateStatusRequest()
    print(st.get_system_update_status(request))

def install_system_update(st):
    request = hostservices_pb2.SystemUpdateInstallRequest()
    print(st.install_system_update(request))


def is_service_running(st, service):
    request = hostservices_pb2.ServiceRunningRequest()
    request.service = service
    print(st.is_service_running(request))


def get_disk_info(st):
    request = hostservices_pb2.DiskInfoRequest()
    print(st.get_disk_info(request))


def get_ip(st):
    request = hostservices_pb2.IpRequest()
    print(st.get_ip(request))


def check_for_system_update(st):
    request = hostservices_pb2.SystemUpdateCheckRequest()
    print(st.check_for_system_update(request))


def get_system_update_status(st):
    request = hostservices_pb2.SystemUpdateStatusRequest()
    print(st.get_system_update_status(request))


def install_system_update(st):
    request = hostservices_pb2.SystemUpdateInstallRequest()
    print(st.install_system_update(request))


if __name__ == '__main__':
    channel = grpc.insecure_channel('localhost:7002')
    stub = hostservices_pb2_grpc.MoblabHostServiceStub(channel)
    get_host_identifier(stub)
    is_service_running(stub, 'moblab-dockerd')
    get_disk_info(stub)
    get_ip(stub)
    check_for_system_update(stub)
    get_system_update_status(stub)
    # This will update your moblab to the latest stable - dont do it if you are not sure
    # you can rollback if you do it by accident.
    # install_system_update(stub)
