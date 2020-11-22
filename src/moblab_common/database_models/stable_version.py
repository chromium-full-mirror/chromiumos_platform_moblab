# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


class StableVersion(declarative_base()):
    __tablename__ = "afe_stable_versions"

    id = Column(Integer, primary_key=True)
    board = Column(String(length=255), nullable=False)
    version = Column(String(length=255), nullable=False)
    archive_url = Column(Text, default=False)
