# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class JobHandoff(declarative_base()):
    """Jobs that have been handed off to lucifer."""

    __tablename__ = "afe_job_handoffs"

    job_id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    completed = Column(Boolean, nullable=False)
    drone = Column(String(length=120), default=None)
