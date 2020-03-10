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


if __name__ == '__main__':
    channel = grpc.insecure_channel('localhost:7002')
    stub = hostservices_pb2_grpc.MoblabHostServiceStub(channel)
    get_host_identifier(stub)
