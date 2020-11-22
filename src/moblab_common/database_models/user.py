# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from database_models.common.constants import Constants
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy import SmallInteger
from sqlalchemy.ext.declarative import declarative_base


class User(declarative_base()):
    """
    Required:
    login :user login name

    Optional:
    access_level: 0=User (default), 1=Admin, 100=Root
    """

    __tablename__ = "afe_users"

    ACCESS_ROOT = 100
    ACCESS_ADMIN = 1
    ACCESS_USER = 0

    AUTOTEST_SYSTEM = "autotest_system"

    id = Column(Integer, primary_key=True)
    login = Column(String(length=255), unique=True)
    access_level = Column(Integer, default=ACCESS_USER)
    reboot_before = Column(
        SmallInteger, default=Constants.REBOOT_BEFORE.IF_DIRTY
    )
    reboot_before = Column(SmallInteger, default=Constants.REBOOT_AFTER.NEVER)
    show_experimental = Column(Boolean, default=False)
    drone_set_id = Column(Integer, default=None)
