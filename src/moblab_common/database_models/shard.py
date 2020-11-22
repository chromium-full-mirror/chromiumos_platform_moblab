# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class Shard(declarative_base()):
    __tablename__ = "afe_shards"
    name_field = "hostname"

    id = Column(Integer, primary_key=True)
    hostname = Column(String(length=255), unique=True)
