# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import asyncio
from unittest import mock, IsolatedAsyncioTestCase

from storage_qual_check_service import (
    StorageQualCheckService,
    StorageQualCheckError,
)


# ToDO: Refactor MoblabService to move label processing methods out
# and refactor these tests to mock the whole MoblabService class.
@mock.patch("moblab_service.MoblabService")
class StorageQualCheckServiceTest(IsolatedAsyncioTestCase):
    """Testing the StorageQualCheckService code."""

    async def test_check_works(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["pool:{}".format(pool), "model:{}".format(model), "board:{}".format(board)]
        # v1
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["dut:1"] + labels,
                    "hostname": "A",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "B",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        await service.check_setup(model, board, pool)

    async def test_check_no_pool_raises_exception(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["model:{}".format(model), "board:{}".format(board)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["dut:1"] + labels,
                    "hostname": "A",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "B",
                    "enrolled": True
                },
                {
                    "labels": ["dut:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(model, board, None)

    async def test_check_raises_exception_without_model(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["board:{}".format(board), "pool:{}".format(pool)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": [ "dut:1"] + labels,
                    "hostname": "A",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "B", 
                    "enrolled": True
                },
                {
                    "labels": ["dut:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(None, board, pool)

    async def test_check_raises_exception_without_board(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["model:{}".format(board), "pool:{}".format(pool)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["dut:1"] + labels,
                    "hostname": "A",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "B", 
                    "enrolled": True
                },
                {
                    "labels": ["dut:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(model, None, pool)


    async def test_check_case_insensitive(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["pool:{}".format(pool), "model:{}".format(model), "board:{}".format(board)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["DUT:1"] + labels,
                    "hostname": "A",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "B",
                    "enrolled": True,
                },
                {
                    "labels": ["DUT:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        await service.check_setup(model, board, pool)

    async def test_check_duplicated_labels(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["pool:{}".format(pool), "model:{}".format(model), "board:{}".format(board)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "A",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "B",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(model, board, pool)

    async def test_check_multiple_labels_on_one_dut(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["pool:{}".format(pool), "model:{}".format(model), "board:{}".format(board)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["trim", "dut:1", "dut:2"] + labels,
                    "hostname": "A",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(model, board, pool)

    async def test_check_missing_label(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["pool:{}".format(pool), "model:{}".format(model), "board:{}".format(board)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "A",
                    "enrolled": True,
                },
                {
                    "labels": ["dut"] + labels,
                    "hostname": "B",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(model, board, pool)

    async def test_check_excludes_not_enrolled(self, mock_service):
        model = "Dirinboz"
        board = "zork"
        pool = "p1"
        labels = ["pool:{}".format(pool), "model:{}".format(model), "board:{}".format(board)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["dut:1"] + labels,
                    "hostname": "A1",
                    "enrolled": False,
                },
                {
                    "labels": ["dut:2"] + labels,
                    "hostname": "B2",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:3"] + labels,
                    "hostname": "C",
                    "enrolled": True,
                },
            ]
        )

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(model, board, pool)

    async def test_check_there_has_enough_same_model_and_board_duts(self, mock_service):
        model_1 = "Dirinboz"
        board_1 = "zork"
        model_2 = "rammus"
        board_2 = "Leona"
        pool = "p1"
        first_labels = ["pool:{}".format(pool), "model:{}".format(model_1), "board:{}".format(board_1)]
        second_labels = ["pool:{}".format(pool), "model:{}".format(model_2), "board:{}".format(board_2)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": [ "dut:1"] + first_labels,
                    "hostname": "A1",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:2"] + first_labels,
                    "hostname": "B2",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:3"] + first_labels,
                    "hostname": "C",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:1"] + second_labels,
                    "hostname": "A1",
                    "enrolled": True,
                }
            ]
        )

        service = StorageQualCheckService()
        await service.check_setup(model_1, board_1, pool)    
    
    async def test_check_there_has_not_enough_same_model_and_board_duts(self, mock_service):
        model_1 = "Dirinboz"
        board_1 = "zork"
        model_2 = "rammus"
        board_2 = "Leona"
        pool = "p1"
        first_labels = ["pool:{}".format(pool), "model:{}".format(model_1), "board:{}".format(board_1)]
        second_labels = ["pool:{}".format(pool), "model:{}".format(model_2), "board:{}".format(board_2)]
        mock_service.return_value.list_duts.return_value = self.future_wrapper(
            [
                {
                    "labels": ["dut:1"] + first_labels,
                    "hostname": "A1",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:2"] + first_labels,
                    "hostname": "B2",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:3"] + first_labels,
                    "hostname": "C",
                    "enrolled": True,
                },
                {
                    "labels": ["dut:1"] + second_labels,
                    "hostname": "A1",
                    "enrolled": True,
                }
            ]
        )

        service = StorageQualCheckService()
        with self.assertRaises(StorageQualCheckError):
            await service.check_setup(model_2, board_2, pool)

    def future_wrapper(self, value):
        f = asyncio.Future()
        f.set_result(value)
        return f
