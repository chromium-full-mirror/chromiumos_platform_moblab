# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base


class AbortedHostQueueEntry(declarative_base()):
    """Represents an aborted host queue entry."""
    __tablename__ = 'afe_aborted_host_queue_entries'

    queue_entry_id = Column(Integer, primary_key=True)
    aborted_by_id = Column(Integer, default=None)
    aborted_on = Column(DateTime, nullable=False)

    def save(self, *args, **kwargs):
        self.aborted_on = datetime.now()
        super(AbortedHostQueueEntry, self).save(*args, **kwargs)
