# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class JobKeyval(declarative_base()):
    """Keyvals associated with jobs"""

    __tablename__ = "afe_job_keyvals"

    SERIALIZATION_LINKS_TO_KEEP = {"job"}
    SERIALIZATION_LOCAL_LINKS_TO_UPDATE = {"value"}

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, nullable=False)
    key = Column(String(length=90), nullable=False)
    value = Column(String(length=300), nullable=False)
