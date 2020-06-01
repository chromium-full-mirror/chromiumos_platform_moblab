from moblab_common import afe_connector
from moblab_common import config_connector

import BaseCollectService


class MoblabCollectService(BaseCollectService):

    def __init__(self):
        self.afe_connector = afe_connector.AFEConnector()
        self.config_connector = config_connector.MoblabConfigConnector(
            self.afe_connector)

    def collect(self):
        raise NotImplementedError()
