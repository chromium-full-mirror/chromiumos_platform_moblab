# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from google.protobuf.json_format import MessageToJson, Parse

from moblab_common.afe_connector import AFEConnector
from settings_store import SettingsStore
from moblab_common.proto.moblab_settings_pb2 import (
    MoblabSettingKey,
    MoblabSetting,
    Value,
)

import logging

LOCK_HOST = True
UNLOCK_HOST = False

PAUSED_DUT_LOCKING_REASON = "Locked by system. Do not change manually"


class PauseServiceException(Exception):
    pass


class HostSchedulerPauseService:
    """Service that manages pausing of host scheduling.
    Effectively allows to pause/resume all running test suites execution.
    """

    def __init__(self):
        self._settings_store = SettingsStore()
        self._afe_connector = AFEConnector()

    def pause_moblab(self, requestor_setting):
        """Commands to pause the host scheduling.

        Arg:
            requestor_setting (MoblabSettingKey): indicate who is
            requesting to pause.

        Returns:
            The list of MoblabSettingKey who is currently requesting to pause.
        """
        pause_status = self.get_pause_status()

        logging.debug(
            "Pause requested: %s; Current pause_status: %s",
            requestor_setting,
            pause_status,
        )
        # make sure is not yet paused by the requestor
        if requestor_setting in pause_status:
            return pause_status

        # find all DUTs' IPs
        hostnames = self._get_all_hosts()

        # make sure not paused yet and there are DUTs to be paused
        if not pause_status and hostnames:
            error = self._afe_connector.modify_hosts_lock_state(
                LOCK_HOST, hostnames, PAUSED_DUT_LOCKING_REASON
            )
            if error:
                raise PauseServiceException(
                    "Failed to pause host scheduler. %s",
                    error.get("message", ""),
                )

        self._set_pause_setting(is_paused=True, requestor=requestor_setting)
        return self.get_pause_status()

    def unpause_moblab(self, requestor_setting):
        """Commands to resume the host scheduling.

        Arg:
            requestor_setting (MoblabSettingKey): indicates who is withdrawing
            pause request.

        Returns:
            The list of requestors (MoblabSettingKey)
            currently requesting to pause.
        """
        pause_status = self.get_pause_status()

        logging.debug(
            "Unpause requested: %s; Current pause_status: %s",
            requestor_setting,
            pause_status,
        )
        # make sure is paused by the requestor
        if requestor_setting not in pause_status:
            return pause_status

        # find all DUTs' IPs
        hostnames = self._get_all_hosts()

        # make sure nothig else holds active pause request
        # and there are DUTs to be unpaused
        if len(pause_status) == 1 and hostnames:
            error = self._afe_connector.modify_hosts_lock_state(
                UNLOCK_HOST, hostnames, ""
            )
            if error:
                raise PauseServiceException(
                    "Failed to unpause host scheduler. %s",
                    error.get("message", ""),
                )

        self._set_pause_setting(is_paused=False, requestor=requestor_setting)
        return self.get_pause_status()

    def ensure_duts_pause_state(self, hostnames: [str]) -> None:
        """Enforces consistent state of host scheduling pause across all DUTs.
        Should be called when new DUT is enrolled.

        Arg:
            hostnames ([str]): optional list of host names

        Returns None.
        """
        pause_status = self.get_pause_status()

        logging.debug(
            "ensure_duts_pause_state called with %s; "
            "Current pause_status: %s",
            hostnames,
            pause_status,
        )
        if not hostnames:
            return []

        if pause_status:
            error = self._afe_connector.modify_hosts_lock_state(
                LOCK_HOST, hostnames, PAUSED_DUT_LOCKING_REASON
            )
            if error:
                raise PauseServiceException(
                    "Failed to pause host scheduler. %s",
                    error.get("message", ""),
                )

        else:
            error = self._afe_connector.modify_hosts_lock_state(
                UNLOCK_HOST, hostnames, ""
            )
            if error:
                raise PauseServiceException(
                    "Failed to unpause host scheduler. %s",
                    error.get("message", ""),
                )

    def get_pause_status(self):
        """Get a list of requestors who is currently requesting to pause.

        Returns:
            The list of PauseRequestor.
        """
        keys = [
            MoblabSettingKey.Name(
                MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE
            ),
            MoblabSettingKey.Name(
                MoblabSettingKey.MOBLAB_SETTING_PAUSED_BY_USER
            ),
        ]

        serialized_values = self._settings_store.get_settings(keys)
        if serialized_values:
            settings = [Parse(sv, MoblabSetting()) for sv in serialized_values]
            return [
                setting.key for setting in settings if setting.value.bool_value
            ]
        return []

    def _get_all_hosts(self):
        duts = self._afe_connector.get_connected_devices()
        return [dut["hostname"] for dut in duts]

    def _set_pause_setting(self, is_paused, requestor):
        setting = MoblabSetting(
            key=MoblabSettingKey.Name(requestor),
            value=Value(bool_value=is_paused),
        )
        serialized_value = MessageToJson(setting)
        self._settings_store.set_setting(
            MoblabSettingKey.Name(setting.key), serialized_value
        )
