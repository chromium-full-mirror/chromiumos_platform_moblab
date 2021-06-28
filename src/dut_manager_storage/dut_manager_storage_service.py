# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from moblab_common import afe_connector


class DutManagerStorageService(object):
    """Class that implements the storage service which interacts with the db.

    This will be the layer that directly interact with the database for the
    managed DUTS.
    """

    def __init__(self):
        """Initialize the connector that interacts with autotest afe server."""
        self.afe_connector = afe_connector.AFEConnector()

    def CreateDut(self, dut):
        pass

    def DeleteDut(self, dut_name):
        pass

    def ListDut(self):
        pass

    def GetDut(self, dut_name):
        pass

    def UpdateDut(self, dut, field_to_update):
        pass
