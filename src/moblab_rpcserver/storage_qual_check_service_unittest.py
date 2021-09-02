# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from unittest import mock, IsolatedAsyncioTestCase

from storage_qual_check_service import (
    StorageQualCheckService,
    StorageQualCheckError,
)


# ToDO: Refactor MoblabService to move label processing methods out
# and refactor these tests to mock the whole MoblabService class.
@mock.patch("moblab_service.MoblabService.list_duts")
class StorageQualCheckServiceTest(IsolatedAsyncioTestCase):
    """Testing the StorageQualCheckService code."""

    async def test_check_works(self, mock_list_duts):
        mock_list_duts.return_value = [
            {
                "labels": ["retention", "pool:p1"],
                "hostname": "A",
                "enrolled": True,
            },
            {
                "labels": ["trim", "pool:p1"],
                "hostname": "B",
                "enrolled": True,
            },
            {
                "labels": ["suspend", "pool:p1"],
                "hostname": "C",
                "enrolled": True,
            },
        ]

        service = StorageQualCheckService()
        await service.check_setup("p1")

    async def test_check_no_pool_raises_exception(self, mock_list_duts):
        mock_list_duts.return_value = [
            {
                "labels": ["retention"],
                "hostname": "A",
                "enrolled": True,
            },
            {"labels": ["trim"], "hostname": "B", "enrolled": True},
            {
                "labels": ["suspend"],
                "hostname": "C",
                "enrolled": True,
            },
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(None)

    async def test_check_case_insensitive(self, mock_list_duts):
        mock_list_duts.return_value = [
            {
                "labels": ["RETENTION", "pool:p1"],
                "hostname": "A",
                "enrolled": True,
            },
            {"labels": ["TRIM", "pool:p1"], "hostname": "B", "enrolled": True},
            {
                "labels": ["suspend", "pool:p1"],
                "hostname": "C",
                "enrolled": True,
            },
        ]

        service = StorageQualCheckService()
        await service.check_setup("p1")

    async def test_check_duplicated_labels(self, mock_list_duts):
        mock_list_duts.return_value = [
            {"labels": ["trim", "pool:p1"], "hostname": "A", "enrolled": True},
            {"labels": ["trim", "pool:p1"], "hostname": "B", "enrolled": True},
            {
                "labels": ["suspend", "pool:p1"],
                "hostname": "C",
                "enrolled": True,
            },
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup("p1")

    async def test_check_multiple_labels_on_one_dut(self, mock_list_duts):
        mock_list_duts.return_value = [
            {
                "labels": ["retention", "trim", "pool:p1"],
                "hostname": "A",
                "enrolled": True,
            },
            {
                "labels": ["suspend", "pool:p1"],
                "hostname": "C",
                "enrolled": True,
            },
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup("p1")

    async def test_check_missing_label(self, mock_list_duts):
        mock_list_duts.return_value = [
            {"labels": ["trim", "pool:p1"], "hostname": "A", "enrolled": True},
            {
                "labels": ["label1", "pool:p1"],
                "hostname": "B",
                "enrolled": True,
            },
            {
                "labels": ["suspend", "pool:p1"],
                "hostname": "C",
                "enrolled": True,
            },
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup("p1")

    async def test_check_excludes_not_enrolled(self, mock_list_duts):
        mock_list_duts.return_value = [
            {
                "labels": ["retention", "pool:1"],
                "hostname": "A1",
                "enrolled": False,
            },
            {
                "labels": ["trim", "pool:1"],
                "hostname": "B2",
                "enrolled": True,
            },
            {
                "labels": ["suspend", "pool:1"],
                "hostname": "C",
                "enrolled": True,
            },
        ]

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup("1", 1)

    async def test_check_bypassed_for_new_storage_qual(self, mock_list_duts):
        mock_list_duts.return_value = [
            {
                "labels": ["retention", "pool:1"],
                "hostname": "A1",
                "enrolled": True,
            },
            {
                "labels": ["trim", "pool:1"],
                "hostname": "B1",
                "enrolled": True,
            },
            {"labels": ["suspend"], "hostname": "C", "enrolled": True},
        ]

        service = StorageQualCheckService()
        await service.check_setup("1", 4)
