# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for the remote requests module."""


# pylint: disable=no-name-in-module, import-error
from google.cloud import exceptions

from moblab_common import versioned_upload

import moblab_request_pb2
import run_suite_request

import logging


class UnknownRequestType(Exception):
    """Custom Exception Type for Unknown Request Type."""

    pass


class MoblabRemoteRequests(object):
    """Class the wraps around a list of remote requests."""

    def __init__(self):
        """Initialize an empty list of requests."""
        self.requests = []

    def add_request(self, request):
        """Add a request to the list of requests.

        Args:
            request (object): A request object derived from MoblabRequest
        """

        if not request in self.requests:
            self.requests.append(request)

    def load_requests_from_gcs(self, blob):
        """Retrieve the serialized output of the request from cloud storage.

        Args:
            blob (object): a cloud storage blob that points to a serialized
                list of requests.

        Returns:
            boolean: True if successful otherwise False.
        """
        try:
            serialized_proto = blob.download_as_string()
        except exceptions.NotFound as e:
            logging.debug(e)
            logging.error("No request list found in %s", blob.path)
            return False

        requests = moblab_request_pb2.MoblabRequests()
        requests.ParseFromString(serialized_proto)

        for suite_request in requests.suite_requests:
            self.requests.append(
                run_suite_request.MoblabSuiteRunRequestWrapper(proto=suite_request)
            )
        return True

    def save_requests_to_gcs(self, blob):
        """Serialize and write the requests to a google cloud storage object.

        Args:
            blob (object): a cloud storage blob.
        """
        requests = moblab_request_pb2.MoblabRequests()
        for request in self.requests:
            if isinstance(request, run_suite_request.MoblabSuiteRunRequestWrapper):
                proto = requests.suite_requests.add()
            else:
                raise UnknownRequestType(request)
            request.copy_to_proto(proto)
        versioned_upload.upload_from_string(blob, requests.SerializeToString())

    def filter_requests(self, filter_func):
        """Remove unwanted items from the list of request.

        filter_func takes a request as a param and returns True or False, any
        functions returning False will be removed from the list of requests.

        Args:
            filter_func (function): function that takes request as a param, and
                returns True or False.
        """
        self.requests = [request for request in self.requests if filter_func(request)]

    def sort_requests(self):
        """Sort requests based on priority.

        Lower priority items are first in the list.
        """

        def get_sort_key(request):
            # TODO(haddowk), after priority use expire time as a second
            # dimension.
            return request.priority

        if self.requests:
            self.requests.sort(key=get_sort_key)

    def get_request(self, index=0):
        """Get a request from the list of requests.

            index (int, optional): Defaults to 0. Zero based index of the
                request requested.

        Returns:
            object: the request object if the index is in range otherwise None.
        """
        try:
            return self.requests[index]
        except IndexError:
            return None

    def __str__(self):
        """Create a more readable string for debugging.

        Returns:
            string: A line for each request.
        """
        output = "Requests:\n"
        for request in self.requests:
            output += "%s\n" % request
        return output
