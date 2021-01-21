# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import logging
import collections

from google.protobuf.json_format import MessageToJson, Parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from moblab_common.database_models.moblab_settings import MoblabSettings
from moblab_common.proto.moblab_settings_pb2 import (
    MoblabSettingKey,
    MoblabSetting,
    Value,
)


class MoblabDb:
    # ToDo push configuration to env vars
    _engine = create_engine(
        "mysql+pymysql://root:moblab_db_passwd@db:3306/moblab", echo=False
    )
    _Session = sessionmaker(bind=_engine)

    def get_session(self):
        return MoblabDb._Session()


class MoblabSettingsStore:
    """Abstraction around persistence layer"""

    def __init__(self):
        self.db = MoblabDb()

    def get_settings(self, keys: [str]) -> [MoblabSettings]:
        """Returns the list of MoblabSettings"""
        if keys:
            session = self.db.get_session()
            results = (
                session.query(MoblabSettings)
                .filter(MoblabSettings.key.in_(keys))
                .all()
            )
            session.close()
            return results
        return None

    def set_setting(
        self,
        key: [str],
        value: [str],
    ) -> None:
        """Create or update setting by key.
        Args:
            key: string that uniquely identifies the setting;
            value: user value;
        """
        session = self.db.get_session()
        try:
            setting = session.query(MoblabSettings).filter_by(key=key).first()
            if not setting:
                logging.info('Insert setting "%s" = "%s"', key, value)
                session.add(
                    MoblabSettings(
                        key=key,
                        value=value,
                    )
                )
            else:
                logging.info(
                    'Updating setting "%s" "%s" -> "%s"',
                    key,
                    setting.value,
                    value,
                )
                setting.value = value
            session.commit()
        finally:
            session.close()


class SettingsService:
    """Provides a proto messages abstraction layer of moblab settings"""

    def __init__(self):
        self._settings_store = MoblabSettingsStore()

    def get_settings(self, keys: [MoblabSettingKey]) -> [MoblabSetting]:
        """Read MoblabSetting from persistence layer.

        Returns:
            The list of MoblabSetting objects.
        """
        string_keys = [MoblabSettingKey.Name(key) for key in keys]

        logging.debug("inside get_settings(%s)", string_keys)

        moblab_settings = self._settings_store.get_settings(string_keys)
        if moblab_settings:
            return [Parse(s.value, MoblabSetting()) for s in moblab_settings]
        return []

    def set_setting(self, setting: MoblabSetting):
        """Persist MoblabSetting."""
        serialized_value = MessageToJson(setting)
        self._settings_store.set_setting(
            MoblabSettingKey.Name(setting.key), serialized_value
        )
