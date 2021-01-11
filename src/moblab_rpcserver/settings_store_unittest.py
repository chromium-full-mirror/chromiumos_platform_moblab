# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import unittest
from unittest import mock

import settings_store


@mock.patch.object(settings_store.MoblabDb, "get_session")
class SettingsStoreTest(unittest.TestCase):
    """Testing the MoblabSettingsStore code."""

    def test_get_settings(self, mock_get_session):
        session_mock = mock.MagicMock()
        mock_get_session.return_value = session_mock

        store = settings_store.MoblabSettingsStore()
        store.get_settings("some_key")

        session_mock.close.assert_called_once()
        mock_get_session.assert_called_once()

    def test_set_settings(self, mock_get_session):
        session_mock = mock.MagicMock()
        mock_get_session.return_value = session_mock

        store = settings_store.MoblabSettingsStore()
        store.set_setting("some_key", "same_value")

        session_mock.commit.assert_called_once()
        session_mock.close.assert_called_once()
        mock_get_session.assert_called_once()

    def test_set_settings_handles_errors(self, mock_get_session):
        session_mock = mock.MagicMock()
        session_mock.query.side_effect = Exception("Test error")
        mock_get_session.return_value = session_mock

        store = settings_store.MoblabSettingsStore()
        with self.assertRaises(Exception):
            store.set_setting("some_key", "same_value")

        session_mock.commit.assert_not_called()
        session_mock.close.assert_called_once()
        mock_get_session.assert_called_once()
