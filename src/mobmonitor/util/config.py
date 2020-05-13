# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import configparser

class Config:
    """
    Provide an interface to read and get config values from
    moblab
    """

    GLOBAL_CONFIG = '/usr/local/autotest/global_config.ini'
    MOBLAB_CONFIG = '/usr/local/autotest/moblab_config.ini'
    SHADOW_CONFIG = '/usr/local/autotest/shadow_config.ini'

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(
            [self.GLOBAL_CONFIG, self.MOBLAB_CONFIG, self.SHADOW_CONFIG])

    def get(self, key):
        """
        Get the specified config value

        Args:
            key: string which config value to get

        Return:
            string containing the config value, or None if no value is set
        """
        # TODO haddowk/mattmallett refactor this to use the "autotest"
        #   interface when that work is completed
        for section in self.config.sections():
            for option, value in self.config.items(section):
                if key == option:
                    return value
        return None


