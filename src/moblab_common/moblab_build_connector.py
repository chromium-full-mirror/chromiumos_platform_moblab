# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""
Interface for the Moblab RPC server to access build resources by using Moblab
API.
"""

import logging
import re

import google.api_core.path_template

from google.auth import exceptions as auth_exceptions
from google.chromeos.moblab_v1beta1.services.build_service.client import \
    BuildServiceClient
from google.chromeos.moblab_v1beta1.types import build_service
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore


class MoblabBuildConnectorException(Exception):
    """Generic exception for this module."""
    pass


class MoblabBuildConnector(object):
    """
    Class that provides RPC server an interface to access build resources by
    using Moblab API.
    """

    @classmethod
    def model_path(cls, build_target, model):
        """Return a fully-qualified model string."""
        return google.api_core.path_template.expand(
            'buildTargets/{build_target}/models/{model}',
            build_target=build_target,
            model=model,
        )

    @classmethod
    def build_artifact_path(cls, build_target, model, build, artifact):
        """Return a fully-qualified build_artifact string."""
        return google.api_core.path_template.expand(
            'buildTargets/{build_target}/models/{model}/builds/{build}/artifacts/{artifact}',
            build_target=build_target,
            model=model,
            build=build,
            artifact=artifact,
        )

    def _parse_milestone(self, milestone):
        if re.match('\Amilestones\/(\d+)$', milestone):
            return 'R' + milestone.split('/')[1]
        else:
            raise MoblabBuildConnectorException(
                'Encountered unexpected format while reading milestones: {}'.format(milestone))

    def __init__(self, build_service_client=None):
        """Instantiates the build connector and sets up the build service
        client. The service account is set in the global environment.
        """
        try:
            self.build_service_client = build_service_client if \
                build_service_client is not None else BuildServiceClient()
        except auth_exceptions.DefaultCredentialsError as e:
            raise MoblabBuildConnectorException('No credentials loaded') from e

    def list_available_milestones(self, build_target, model, page_size=50,
        page_token=None):
        """Lists the available milestones for the given build target and model.

        Args:
            build_target (str): Build target name.
            model (str): Model name. For non-unibuilds, set the model name as
                the same as build target name.
            page_size (int): The number of milestones to return in the response.
                The default size is 50.
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
            group_by=milestone_field
        )
        build_results = self.build_service_client.list_builds(request).builds
        return [self._parse_milestone(build.milestone) for build in build_results]

    def list_builds_for_milestone(self, build_target, model, milestone,
        page_size=50, page_token=None):
        """Lists the builds for the given build target, model and milestone.

        Args:
            build_target (str): The build target name.
            model (str): The model name. For non-unibuilds, set the model name as
                the same as build target name.
            milestone (int): The milestone number.
            page_size (int): The number of milestones to return in the response.
                The default size is 50.
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
            filter=milestone_filter
        )
        build_results = self.build_service_client.list_builds(request).builds
        return [build.build_version for build in build_results]

    def check_build_stage_status(self, build_target, model, build, bucket_name):
        """Checks the stage status for a given build artifact in a partner
        Google Cloud Storage bucket.

        Args:
            build_target (str): The build target name.
            model (str): The model name. For non-unibuilds, set the model name as
                the same as build target name.
            build (str): The build version.
            bucket_name: The destination bucket name .

        Returns:
            build_service.CheckBuildStageStatusResponse: Response message for
            check the stage status of a build artifact.
        """
        request = build_service.CheckBuildStageStatusRequest(
            name=self.build_artifact_path(build_target, model, build,
                                          bucket_name)
        )
        return self.build_service_client.check_build_stage_status(request)

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
            name=self.build_artifact_path(build_target, model, build,
                                          bucket_name)
        )
        return self.build_service_client.stage_build(request)
