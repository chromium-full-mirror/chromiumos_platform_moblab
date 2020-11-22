# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class HostQueueEntry(declarative_base()):
    """Represents a host queue entry."""

    __tablename__ = "afe_host_queue_entries"

    SERIALIZATION_LINKS_TO_FOLLOW = {"meta_host"}
    SERIALIZATION_LINKS_TO_KEEP = {"host"}
    SERIALIZATION_LOCAL_LINKS_TO_UPDATE = {"aborted"}

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, nullable=False)
    host_id = Column(Integer, nullable=False)
    status = Column(String(length=255), default=False)
    meta_host = Column(Integer, default=None)
    active = Column(Boolean, default=0)
    complete = Column(Boolean, default=0)
    deleted = Column(Boolean, nullable=False)
    execution_subdir = Column(String(length=255), nullable=False)
    atomic_group_id = Column(Integer, default=None)
    aborted = Column(Boolean, nullable=False, default=0)
    started_on = Column(DateTime, default=None)
    finished_on = Column(DateTime, default=None)
