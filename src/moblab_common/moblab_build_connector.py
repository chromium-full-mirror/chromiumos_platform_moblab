# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""
Interface for the Moblab RPC server to access build resources by using Moblab
API.
"""

import collections
import enum
import logging
import re

import google.api_core.path_template

from google.api_core import exceptions as api_exceptions
from google.auth import exceptions as auth_exceptions
from google.chromeos.moblab_v1beta1.services.build_service.client import (
    BuildServiceClient,
)
from google.chromeos.moblab_v1beta1.types import build_service, resources
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from functools import wraps

DEFAULT_PAGE_SIZE = 500


class MoblabBuildConnectorException(Exception):
    """Generic exception for this module."""
    pass


class ArgumentException(Exception):
    pass


class GoogleApiException(Exception):
    pass


BuildStatus = enum.Enum(
    "BuildStatus", ["AVAILABLE", "FAILED", "RUNNING", "ABORTED"]
)

BuildVersion = collections.namedtuple("BuildVersion", ["version", "status"])

API_TO_INTERNAL_BUILD_STATUS_MAP = {
    resources.Build.BuildStatus.PASS: BuildStatus.AVAILABLE,
    resources.Build.BuildStatus.FAIL: BuildStatus.FAILED,
    resources.Build.BuildStatus.RUNNING: BuildStatus.RUNNING,
    resources.Build.BuildStatus.ABORTED: BuildStatus.ABORTED,
}


def exception_handler(unhandled_exception_message: str):
    def decorator(func):
        @wraps(func)
        def result(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except auth_exceptions.DefaultCredentialsError as e:
                msg = "Invalid Credentials"
                logging.info(msg + f" reason: {e}")
                raise MoblabBuildConnectorException(msg)
            except api_exceptions.Forbidden as e:
                msg = "Request to gcs bucket got Forbidden error"
                logging.info(msg + f" reason: {e}")
                raise GoogleApiException(msg)
            except api_exceptions.ResourceExhausted as e:
                msg = "Request to gcs bucket got ResourceExhausted error"
                logging.info(msg + f" reason: {e}")
                raise GoogleApiException(msg)
            except (api_exceptions.Unauthorized, api_exceptions.Unauthenticated) as e:
                msg = "Request to gcs bucket got an Unauthorized error"
                logging.info(msg + f" reason: {e}")
                raise GoogleApiException(msg)
            except ArgumentException as e:
                raise
            except GoogleApiException as e:
                raise
            except api_exceptions.GoogleAPICallError as e:
                msg = "Request to gcs bucket failed."
                logging.info(msg + f" reason: {e}")
                raise MoblabBuildConnectorException(msg)
            except Exception as e:
                msg = f"Request to gcs bucket caught an unknown exception: {e}"
                logging.info(msg)
                raise MoblabBuildConnectorException(unhandled_exception_message)
        return result
    return decorator



class MoblabBuildConnector(object):
    """
    Class that provides RPC server an interface to access build resources by
    using Moblab API.
    """

    @classmethod
    def build_target_path(cls, build_target):
        """Return a fully-qualified build_target string."""
        return google.api_core.path_template.expand(
            "buildTargets/{build_target}",
            build_target=build_target,
        )

    @classmethod
    def model_path(cls, build_target, model):
        """Return a fully-qualified model string."""
        return google.api_core.path_template.expand(
            "buildTargets/{build_target}/models/{model}",
            build_target=build_target,
            model=model,
        )

    @classmethod
    def build_artifact_path(cls, build_target, model, build, artifact):
        """Return a fully-qualified build_artifact string."""
        return google.api_core.path_template.expand(
            "buildTargets/{build_target}/models/{model}/builds/{build}/artifacts/{artifact}",
            build_target=build_target,
            model=model,
            build=build,
            artifact=artifact,
        )

    def _parse_milestone(self, milestone):
        if re.match("\Amilestones\/(\d+)$", milestone):
            return milestone.split("/")[1]
        else:
            raise MoblabBuildConnectorException(
                "Encountered unexpected format while reading milestones: {}".format(
                    milestone
                )
            )

    def __init__(self, build_service_client=None):
        """Instantiates the build connector and sets up the build service
        client. The service account is set in the global environment.
        """
        try:
            self.build_service_client = (
                build_service_client
                if build_service_client is not None
                else BuildServiceClient()
            )
        except auth_exceptions.DefaultCredentialsError as e:
            raise MoblabBuildConnectorException("No credentials loaded") from e

    @exception_handler(unhandled_exception_message="Encountered API error when attempting to list builds.")
    def _list_builds(self, request):
        return self.build_service_client.list_builds(request).builds

    @exception_handler(unhandled_exception_message="Encountered API error when attempting to find the most stable build.")
    def _find_most_stable_build(self, request):
        return self.build_service_client.find_most_stable_build(request).build

    @exception_handler(unhandled_exception_message="Encountered API error when attempting to list build targets.")
    def _list_build_targets(self, request):
        return self.build_service_client.list_build_targets(request).build_targets

    @exception_handler(unhandled_exception_message="Encountered API error when attempting to list models.")
    def _list_models(self, request):
        return self.build_service_client.list_models(request).models

    def list_available_milestones(
        self, build_target, model, page_size=DEFAULT_PAGE_SIZE, page_token=None
    ):
        """Lists the available milestones for the given build target and model.

        Args:
            build_target (str): Build target name.
            model (str): Model name. For non-unibuilds, set the model name as
                the same as build target name.
            page_size (int): The number of milestones to return in the response.
                The default size is DEFAULT_PAGE_SIZE.
            page_token (str): A page token, received from a previous
                ``ListBuilds`` call. Provide this to retrieve the subsequent
                page.

        Returns:
            List of strings representing milestones.
        """
        milestone_field = field_mask.FieldMask(paths=["milestone"])
        request = build_service.ListBuildsRequest(
            parent=self.model_path(build_target, model),
            page_size=page_size,
            page_token=page_token,
            read_mask=milestone_field,
            group_by=milestone_field,
        )
        build_results = self._list_builds(request)
        return [
            self._parse_milestone(build.milestone) for build in build_results
        ]

    def get_most_stable_build(self, build_target):
        """Gets the most stable build for the given build target.

        Args:
            build_target (str): Build target name.

        Returns:
            string: most stable build version.
        """
        request = build_service.FindMostStableBuildRequest(
            build_target=self.build_target_path(build_target),
        )
        build = self._find_most_stable_build(request)
        milestone = self._parse_milestone(build.milestone)
        return "R{}-{}".format(milestone, build.build_version)

    def _convert_to_internal_build_status(self, status):
        if status in API_TO_INTERNAL_BUILD_STATUS_MAP:
            return API_TO_INTERNAL_BUILD_STATUS_MAP[status]
        return BuildStatus.AVAILABLE

    def list_builds_for_milestone(
        self,
        build_target,
        model,
        milestone,
        page_size=DEFAULT_PAGE_SIZE,
        page_token=None,
    ):
        """Lists the builds for the given build target, model and milestone.

        Args:
            build_target (str): The build target name.
            model (str): The model name. For non-unibuilds, set the model name as
                the same as build target name.
            milestone (int): The milestone number.
            page_size (int): The number of milestones to return in the response.
                The default size is DEFAULT_PAGE_SIZE.
            page_token (str): The page token, received from a previous
                ``ListBuilds`` call. Provide this to retrieve the subsequent
                page.

        Returns:
            List of strings representing build versions.
        """
        milestone_filter = "milestone=milestones/" + str(milestone)

        request = build_service.ListBuildsRequest(
            parent=self.model_path(build_target, model),
            page_size=page_size,
            page_token=page_token,
            filter=milestone_filter,
        )
        build_results = self._list_builds(request)
        return [
            BuildVersion(
                version=build.build_version,
                status=self._convert_to_internal_build_status(build.status),
            )
            for build in build_results
        ]

    @exception_handler(unhandled_exception_message="Encountered API error when attempting to check build stage status.")
    def check_build_stage_status(
        self, build_target, model, build, bucket_name
    ):
        """Checks the stage status for a given build artifact in a partner
        Google Cloud Storage bucket.

        Args:
            build_target (str): The build target name. e.g. hatch
            model (str): The model name. For non-unibuilds, set the model name
                as the same as build target name.  e.g. kohaku
            build (str): The build version. e.g. 13816.1.0
            bucket_name: The destination bucket name.
                e.g. chromeos-moblab-peng-staging

        Returns:
            boolean: True iff build is staged ( recognized by the # of objects in the src build directory
                equaling the # of objects in the destination build directory )
        """
        request = build_service.CheckBuildStageStatusRequest(
            name=self.build_artifact_path(
                build_target, model, build, bucket_name
            )
        )
        return self.build_service_client.check_build_stage_status(
            request
        ).is_build_staged

    @exception_handler(unhandled_exception_message="Encountered API error when attempting to stage build.")
    def stage_build(self, build_target, model, build, bucket_name):
        # TODO(zhihuixie): Long running operation cannot returned correctly in
        # the python client library.
        """Stages a given build artifact from a internal Google Cloud Storage
        bucket to a partner Google Cloud Storage bucket. The stage will be
        skipped if all the objects in the partner bucket are the same as in the
        internal bucket.

        Args:
            build_target (str): The build target name.
            model (str): The model name. For non-unibuilds, set the model name as
                the same as build target name.
            build (str): The build version.
            bucket_name: The destination bucket name .

        Returns:
            operation.Operation:
                An object representing a long-running operation. The result
                type for the operation will be
                ``build_service.StageBuildResponse``: Response
                message for staging a build artifact.
        """
        request = build_service.StageBuildRequest(
            name=self.build_artifact_path(
                build_target, model, build, bucket_name
            )
        )
        return self.build_service_client.stage_build(request)

    def list_build_targets(
        self,
        page_size=DEFAULT_PAGE_SIZE,
        page_token=None,
    ):
        """List all build targets that an account has access to.

        Args:
            page_size (int): The number of milestones to return in the response.
                The default size is DEFAULT_PAGE_SIZE.
            page_token (str): The page token, received from a previous
                ``ListBuilds`` call. Provide this to retrieve the subsequent
                page.

        Returns:
            list of string representating the build targets.
        """
        request = build_service.ListBuildTargetsRequest(
            page_size=page_size,
            page_token=page_token,
        )

        build_targets = self._list_build_targets(request)
        return [build_target.name for build_target in build_targets]

    def list_models(
        self,
        build_target="*",
        page_size=DEFAULT_PAGE_SIZE,
        page_token=None,
    ):
        """List all models for a given build targets that an account has access to.

        If the build target is not provided or set to '*',
            it lists models for all build targets.

        Args:
            build_target (str): The build target name.
            page_size (int): The number of milestones to return in the response.
                The default size is DEFAULT_PAGE_SIZE.
            page_token (str): The page token, received from a previous
                ``ListBuilds`` call. Provide this to retrieve the subsequent
                page.

        Returns:
            list of string representating the models path.
        """
        request = build_service.ListModelsRequest(
            parent=self.build_target_path(build_target),
            page_size=page_size,
            page_token=page_token,
        )

        models = self._list_models(request)
        return [model.name for model in models]
