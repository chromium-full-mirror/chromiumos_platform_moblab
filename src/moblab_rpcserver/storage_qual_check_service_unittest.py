# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import unittest
from unittest import mock

from storage_qual_check_service import (
    StorageQualCheckService,
    StorageQualCheckError,
)


@mock.patch("moblab_service.MoblabService")
class StorageQualCheckServiceTest(unittest.TestCase):
    """Testing the StorageQualCheckService code."""

    def test_check_works(self, mock_service):
        mock_service.return_value.list_duts.return_value = [
            {"labels": ["retention"], "hostname": "A"},
            {"labels": ["trim"], "hostname": "B"},
            {"labels": ["suspend"], "hostname": "C"},
        ]

        service = StorageQualCheckService()
        service.check_setup(None)

    def test_check_case_insensitive(self, mock_service):
        mock_service.return_value.list_duts.return_value = [
            {"labels": ["RETENTION"], "hostname": "A"},
            {"labels": ["TRIM"], "hostname": "B"},
            {"labels": ["suspend"], "hostname": "C"},
        ]

        service = StorageQualCheckService()
        service.check_setup(None)

    def test_check_duplicated_labels(self, mock_service):
        mock_service.return_value.list_duts.return_value = [
            {"labels": ["trim"], "hostname": "A"},
            {"labels": ["trim"], "hostname": "B"},
            {"labels": ["suspend"], "hostname": "C"},
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            service.check_setup(None)

    def test_check_multiple_labels_on_one_dut(self, mock_service):
        mock_service.return_value.list_duts.return_value = [
            {"labels": ["retention", "trim"], "hostname": "A"},
            {"labels": ["suspend"], "hostname": "C"},
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            service.check_setup(None)

    def test_check_missing_label(self, mock_service):
        mock_service.return_value.list_duts.return_value = [
            {"labels": ["trim"], "hostname": "A"},
            {"labels": ["label1"], "hostname": "B"},
            {"labels": ["suspend"], "hostname": "C"},
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            service.check_setup(None)

    def test_no_pool_includes_all_pools(self, mock_service):
        mock_service.return_value.list_duts.return_value = [
            {"labels": ["retention", "pool:1"], "hostname": "A1"},
            {"labels": ["trim", "pool:2"], "hostname": "B2"},
            {"labels": ["suspend"], "hostname": "C"},
        ]

        service = StorageQualCheckService()
        service.check_setup(None)

    def test_check_missing_labels_for_specific_pool(self, mock_service):
        mock_service.return_value.list_duts.return_value = [
            {"labels": ["retention", "pool:1"], "hostname": "A1"},
            {"labels": ["trim", "pool:1"], "hostname": "B1"},
            {"labels": ["suspend"], "hostname": "C"},
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            service.check_setup("1")

    def test_check_duplicated_labels_across_pool_and_no_pool(
        self, mock_service
    ):
        mock_service.return_value.list_duts.return_value = [
            {"labels": ["retention", "pool:1"], "hostname": "A1"},
            {"labels": ["trim", "pool:1"], "hostname": "B1"},
            {"labels": ["trim"], "hostname": "B"},
            {"labels": ["suspend"], "hostname": "C"},
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            service.check_setup(None)
