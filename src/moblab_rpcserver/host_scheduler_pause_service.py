import logging
from google.protobuf.json_format import MessageToJson, Parse


from moblab_common.afe_connector import AFEConnector
from settings_store import SettingsStore
from moblab_common.proto.moblab_configuration_rpc_pb2 import PauseRequestor
from moblab_common.proto.moblab_settings_pb2 import (
    MoblabSettingKey,
    MoblabSetting,
    Value,
)

LOCK_HOST = True
UNLOCK_HOST = False

PAUSED_DUT_LOCKING_REASON = "Locked by system. Do not change manually"


class HostSchedulerPauseService:
    def __init__(self):
        self._settings_store = SettingsStore()
        self._afe_connector = AFEConnector()

    def pause_moblab(self, requestor):
        duts = self._afe_connector.get_connected_devices()
        # ToDo: actually lock duts
        # self._afe_connector.modify_hosts_lock_state(duts, LOCK_HOST, duts, PAUSED_DUT_LOCKING_REASON)

        self._set_pause_setting(is_paused=True, requestor=requestor)
        return self.get_pause_status()

    def unpause_moblab(self, requestor):
        duts = self._afe_connector.get_connected_devices()
        # ToDo: actually unlock duts
        # self._afe_connector.modify_hosts_lock_state(duts, UNLOCK_HOST, duts, '')

        self._set_pause_setting(is_paused=False, requestor=requestor)
        return self.get_pause_status()

    def ensure_duts_pause_state(self):
        is_pause = self.get_pause_status()

        duts = self._afe_connector.get_connected_devices()

        # ToDo: actually lock duts
        # if not is_pause:
        #   self._afe_connector.modify_hosts_lock_state(duts, LOCK_HOST, duts, PAUSED_DUT_LOCKING_REASON)
        # esle
        #   self._afe_connector.modify_hosts_lock_state(duts, UNLOCK_HOST, duts, '')

    def get_pause_status(self):
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
                self._map_to_requestor(setting.key)
                for setting in settings
                if setting.value.bool_value
            ]
        return []

    def _set_pause_setting(self, is_paused, requestor):
        setting = MoblabSetting(
            key=self._map_to_setting(requestor),
            value=Value(bool_value=is_paused),
        )
        serialized_value = MessageToJson(setting)
        self._settings_store.set_setting(
            MoblabSettingKey.Name(setting.key), serialized_value
        )

    def _map_to_setting(self, requestor):
        if requestor == PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE:
            return MoblabSettingKey.Name(
                MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE
            )

        elif requestor == PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER:
            return MoblabSettingKey.Name(
                MoblabSettingKey.MOBLAB_SETTING_PAUSED_BY_USER
            )

    def _map_to_requestor(self, setting_key):
        if setting_key == MoblabSettingKey.MOBLAB_SETTING_LOW_DISK_SPACE:
            return PauseRequestor.Name(
                PauseRequestor.PAUSE_REQUESTOR_LOW_DISK_SPACE
            )

        elif setting_key == MoblabSettingKey.MOBLAB_SETTING_PAUSED_BY_USER:
            return PauseRequestor.Name(
                PauseRequestor.PAUSE_REQUESTOR_PAUSED_BY_USER
            )
