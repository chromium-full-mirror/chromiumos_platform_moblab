import unittest
from unittest import mock

import settings_store


class SettingsStoreTest(unittest.TestCase):
    """Testing the SettingsStore code."""

    @mock.patch.object(settings_store.MoblabDb, "get_session")
    def test_get_settings(self, mock_get_session):
        session_mock = mock.MagicMock()
        mock_get_session.return_value = session_mock

        store = settings_store.SettingsStore()
        store.get_settings("some_key")

        session_mock.close.assert_called_once()
        mock_get_session.assert_called_once()

    @mock.patch.object(settings_store.MoblabDb, "get_session")
    def test_set_settings(self, mock_get_session):
        session_mock = mock.MagicMock()
        mock_get_session.return_value = session_mock

        store = settings_store.SettingsStore()
        store.set_setting("some_key", "same_value")

        session_mock.commit.assert_called_once()
        session_mock.close.assert_called_once()
        mock_get_session.assert_called_once()

    @mock.patch.object(settings_store.MoblabDb, "get_session")
    def test_set_settings_handles_errors(self, mock_get_session):
        session_mock = mock.MagicMock()
        session_mock.query.side_effect = Exception("Test error")
        mock_get_session.return_value = session_mock

        store = settings_store.SettingsStore()
        with self.assertRaises(Exception):
            store.set_setting("some_key", "same_value")

        session_mock.commit.assert_not_called()
        session_mock.close.assert_called_once()
        mock_get_session.assert_called_once()
