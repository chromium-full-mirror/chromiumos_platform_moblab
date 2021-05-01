# -*- coding: utf-8 -*-
# Copyright 2019 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Connector to the autotest configuration settings for all moblab code."""


class MoblabConfigConnector(object):
    """Wrap all config settings access in a single class.

    Eventually moblab configuration options will be
    re-implemented, wrap all moblab config access in a
    single class to make that task easier.
    """

    def __init__(self, afe_connector):
        """Configs are currently accessed from AFE."""
        self.afe_connector = afe_connector
        self.config = None

    def load_config(self):
        """Request configs from AFE."""
        self.config = self.afe_connector.get_config_values()

    def get(self, section, key, default=None, force_reload=False):
        """Get the value of a specific configuration value.

        Args:
            section (string): the section name of the config value to retrieve.
            key (string): the key name of the config value to retrieve.
            default (any, optional): Defaults to None. If the section/key is
                not found in the configuration, return this value.
            force_reload (bool, optional): Defaults to False. By default this
                connector class will cache the results from the AFE, if you
                want that cache to be refreshed then pass in True.

        Returns:
            [type]: [description]
        """
        if not self.config or force_reload:
            self.load_config()
        if not self.config or section not in self.config:
            return default
        return self.config[section].get(key, default)

    def get_cloud_bucket(self, force_reload=False):
        """Get the configured cloud storage bucket name.

        Returns:
            string: The configured cloud storage bucket or None
        """
        # The bucket setting has gs:// and ends in /, so remove them
        image_server = self.get(
            "CROS", "image_storage_server", force_reload=force_reload
        )
        if image_server and len(image_server) > 5:
            return image_server[5:-1]
        else:
            return None

    def is_remote_task_scheduler_enabled(self):
        """Return task scheduler is enabled otherwise false."""
        is_enable = self.get(
            "REMOTE_TASK_SCHEDULER",
            "enabled",
            default=False,
            force_reload=True,
        )
        return True if is_enable == "True" else False

    def get_remote_task_scheduler_tick_delay(self):
        """Return the number of mins task scheduler waits between attempts."""
        return int(self.get("REMOTE_TASK_SCHEDULER", "tick_interval", 30))

    def is_remote_task_debug_enabled(self):
        """Return True if remote task debug is enabled in config."""
        is_enable = self.get(
            "REMOTE_TASK_SCHEDULER", "debug_enabled", default=False
        )
        return True if is_enable == "True" else False

    def get_is_remote_agent_enabled(self):
        """Return if the remote agent is enabled otherwise false."""
        is_enable = self.get(
            "REMOTE_AGENT", "enabled", default=False, force_reload=True
        )
        return True if is_enable == "True" else False
