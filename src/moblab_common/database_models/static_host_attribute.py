# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class StaticHostAttribute(declarative_base()):
    """Static arbitrary keyvals associated with hosts."""

    __tablename__ = "afe_static_host_attributes"

    SERIALIZATION_LINKS_TO_KEEP = {"host"}
    SERIALIZATION_LOCAL_LINKS_TO_UPDATE = {"value"}

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, nullable=False)
    attribute = Column(String(length=90), nullable=False)
    value = Column(String(length=300), nullable=False)
