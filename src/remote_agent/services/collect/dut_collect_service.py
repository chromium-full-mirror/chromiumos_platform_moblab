from moblab_common import afe_connector
from moblab_common import dut_connector

import BaseCollectService


class DutCollectService(BaseCollectService):

    def __init__(self):
        self.afe_connector = afe_connector.AFEConnector()
        self.dut_connector = dut_connector.MoblabDUTConnector()

    def collect(self):
        raise NotImplementedError()
