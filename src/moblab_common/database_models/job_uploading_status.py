# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from moblab_common.database_models.declarative_base import Base


class JobUploadingStatus(Base):
    __tablename__ = "job_uploading_status"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, nullable=False, unique=True)
    status = Column(String(length=255), default=False)
    updated_on = Column(DateTime)
    upload_attempt_number = Column(Integer)
    last_attempt_failure_reason = Column(String(length=255))
