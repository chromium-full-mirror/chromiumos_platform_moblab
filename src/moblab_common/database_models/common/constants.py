# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from database_models.common import enum


class Constants:
    # Common enums for Job attributes
    REBOOT_BEFORE = enum.Enum("Never", "If dirty", "Always")
    REBOOT_AFTER = enum.Enum("Never", "If all tests passed", "Always")
