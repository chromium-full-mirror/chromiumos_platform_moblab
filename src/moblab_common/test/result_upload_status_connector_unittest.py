# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import unittest
from unittest import mock

from moblab_common.result_upload_status_connector import (
    ResultUploadStatusConnector,
    UploadResultState,
    Status,
)
from moblab_common.database_models.job_uploading_status import (
    JobUploadingStatus,
)


class ResultUploadStatusConnectorTest(unittest.TestCase):
    """Testing of ResultUploadStatusConnector class"""

    @mock.patch("moblab_common.result_upload_status_connector.MoblabDb")
    def test_get_jobs_upload_status(self, mock_moblab_db):
        all_result_mock = mock.MagicMock()
        all_result_mock.all.return_value = [
            JobUploadingStatus(
                job_id=1,
                status="UPLOADING",
                upload_attempt_number=4,
                last_attempt_failure_reason="E",
            )
        ]
        filter_result_mock = mock.MagicMock()
        filter_result_mock.filter.return_value = all_result_mock

        query_result_mock = mock.MagicMock()
        query_result_mock.query.return_value = filter_result_mock

        mock_moblab_db.return_value.get_session.return_value = (
            query_result_mock
        )

        connector = ResultUploadStatusConnector()
        result = connector.get_jobs_upload_status([1, 2, 3])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[1].last_falure_reason, "E")
        self.assertEqual(result[1].status, Status.UPLOADING.name)
        self.assertEqual(result[1].attempt_number, 4)