# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base


class IneligibleHostQueue(declarative_base()):
    """Represents an ineligible host queue."""

    __tablename__ = "afe_ineligible_host_queues"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, default=None)
    host_id = Column(Integer, default=None)
