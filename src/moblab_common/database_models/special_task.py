# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from database_models.common import enum


class SpecialTask(declarative_base()):
    """
    Tasks to run on hosts at the next time they are in the Ready state. Use this
    for high-priority tasks, such as forced repair or forced reinstall.

    host: host to run this task on
    task: special task to run
    time_requested: date and time the request for this task was made
    is_active: task is currently running
    is_complete: task has finished running
    is_aborted: task was aborted
    time_started: date and time the task started
    time_finished: date and time the task finished
    queue_entry: Host queue entry waiting on this task (or None, if task was not
                 started in preparation of a job)
    """

    __tablename__ = "afe_special_tasks"

    Task = enum.Enum(
        "Verify", "Cleanup", "Repair", "Reset", "Provision", string_values=True
    )

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, nullable=False)
    task = Column(String(length=64), nullable=False)
    time_requested = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    is_complete = Column(Boolean, nullable=False, default=False)
    time_started = Column(DateTime, default=None)
    queue_entry_id = Column(Integer, default=None)
    success = Column(Boolean, nullable=False)
    requested_by_id = Column(Integer, nullable=False)
    is_aborted = Column(Boolean, nullable=False, default=False)
    time_finished = Column(DateTime, default=None)
