# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unit tests for the moblab_build_connector"""

import unittest
from unittest import mock

from moblab_build_connector import MoblabBuildConnector

from google.chromeos.moblab_v1beta1.types import build_service
from google.chromeos.moblab_v1beta1.types import resources


class MoblabBuildConnectorTest(unittest.TestCase):
    """Testing the MoblabBuildConnector code."""

    BUILD_TARGET = 'octopus'
    MODEL = 'bobba'
    MILESTONE_NO = '80'
    MILESTONE = 'milestones/' + MILESTONE_NO
    BUILD_VERSION = '1234.5.6'
    SOURCE_BUCKET = 'source_bucket'
    DESTINATION_BUCKET = 'destination bucket'

    def setUp(self):
        self.mock_build_service_client = mock.MagicMock()
        self.moblab_build_connector = MoblabBuildConnector(
            self.mock_build_service_client)

    def test_list_available_milestones(self):
        build = resources.Build(
            name=MoblabBuildConnector.model_path(self.BUILD_TARGET, self.MODEL),
            milestone=str(self.MILESTONE))
        expect = self.mock_build_service_client.list_builds.return_value = \
            build_service.ListBuildsResponse(
                builds=[build],
                next_page_token='next_page_token_value',
                total_size=1,
            )

        response = self.moblab_build_connector.list_available_milestones(
            self.BUILD_TARGET, self.MODEL)

        self.assertEqual(response, [self.MILESTONE_NO])
        self.mock_build_service_client.list_builds.assert_called_once()

    def test_list_builds_for_milestone(self):
        build = resources.Build(
            name=MoblabBuildConnector.model_path(self.BUILD_TARGET, self.MODEL),
            milestone=str(self.MILESTONE),
            build_version=self.BUILD_VERSION)
        expect = self.mock_build_service_client.list_builds.return_value = \
            build_service.ListBuildsResponse(
                builds=[build],
                next_page_token='next_page_token_value',
                total_size=1,
            )

        response = self.moblab_build_connector.list_builds_for_milestone(
            self.BUILD_TARGET, self.MODEL, self.MILESTONE)

        self.assertEqual(response, [self.BUILD_VERSION])
        self.mock_build_service_client.list_builds.assert_called_once()

    def test_check_build_stage_status(self):
        staged_build_artifact = resources.BuildArtifact(
            bucket=self.DESTINATION_BUCKET
        )
        source_build_artifact = resources.BuildArtifact(
            bucket=self.SOURCE_BUCKET)
        expect = self.mock_build_service_client.check_build_stage_status.return_value = \
            build_service.CheckBuildStageStatusResponse(
                is_build_staged=True,
                staged_build_artifact=staged_build_artifact,
                source_build_artifact=source_build_artifact
            )

        response = self.moblab_build_connector.check_build_stage_status(
            self.BUILD_TARGET, self.MODEL, self.BUILD_VERSION,
            self.DESTINATION_BUCKET)

        self.assertEqual(response.staged_build_artifact,
                         expect.staged_build_artifact)
        self.mock_build_service_client.check_build_stage_status.assert_called_once()

    def test_stage_build(self):
        staged_build_artifact = resources.BuildArtifact(
            bucket=self.DESTINATION_BUCKET
        )
        expect = self.mock_build_service_client.stage_build.return_value = \
            build_service.StageBuildResponse(
                staged_build_artifact=staged_build_artifact
            )

        response = self.moblab_build_connector.stage_build(
            self.BUILD_TARGET, self.MODEL, self.BUILD_VERSION,
            self.DESTINATION_BUCKET)

        self.assertEqual(response.staged_build_artifact,
                         expect.staged_build_artifact)
        self.mock_build_service_client.stage_build.assert_called_once()


if __name__ == '__main__':
    unittest.main()
