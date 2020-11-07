# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class MoblabSettings(Base):
    __tablename__ = 'moblab_settings'

    id = Column(Integer, primary_key=True)
    key = Column(String(length=255), nullable=False, unique=True)
    value = Column(String(length=max), nullable=False)
    default_value = Column(String(length=max), nullable=False)
    description = Column(Text, default=False)
