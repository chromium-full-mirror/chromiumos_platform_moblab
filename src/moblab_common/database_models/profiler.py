# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


class Profiler(declarative_base()):
    """
    Required:
    name: profiler name
    test_type: Client or Server

    Optional:
    description: arbirary text description
    """
    __tablename__ = 'afe_profilers'
    name_field = 'name'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
