# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base


class HostQueueEntryStartTimes(declarative_base()):
    """An auxiliary table to HostQueueEntry to index by start time."""

    __tablename__ = "afe_host_queue_entry_start_times"

    id = Column(Integer, primary_key=True)
    insert_time = Column(
        DateTime, nullable=False, default=datetime.datetime.now().timestamp()
    )
    highest_hqe_id = Column(Integer, nullable=False)
