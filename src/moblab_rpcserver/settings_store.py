import logging

from moblab_common.database_models.moblab_settings import MoblabSettings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class MoblabDb:
    # ToDo push configuration to env vars
    _engine = create_engine(
        "mysql+pymysql://root:moblab_db_passwd@db:3306/moblab", echo=False
    )
    _Session = sessionmaker(bind=_engine)

    def get_session(self):
        return MoblabDb._Session()


class SettingsStore:
    """Abstraction around persistence layer"""

    def __init__(self):
        self.db = MoblabDb()

    def get_settings(self, keys):
        """Returns the list of active"""
        if keys:
            results = (
                self.db.get_session()
                .query(MoblabSettings)
                .filter(MoblabSettings.key.in_(keys))
                .all()
            )
            if results:
                return [r.value or r.default_value for r in results]
        return None

    def set_setting(self, key, value):
        session = self.db.get_session()
        setting = session.query(MoblabSettings).filter_by(key=key).first()
        if not setting:
            logging.info('Insert setting "%s" = "%s"', key, value)
            session.add(
                MoblabSettings(
                    key=key,
                    value=value,
                    default_value=value,
                )
            )
        else:
            logging.info(
                'Updating setting "%s" "%s" -> "%s"', key, setting.value, value
            )
            setting.value = value
        session.commit()
