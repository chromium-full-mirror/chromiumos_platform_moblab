# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base


class Host(declarative_base()):
    """
    Required:
    hostname

    optional:
    locked: if true, host is locked and will not be queued

    Internal:
    From AbstractHostModel:
        status: string describing status of host
        invalid: true if the host has been deleted
        protection: indicates what can be done to this host during repair
        lock_time: DateTime at which the host was locked
        dirty: true if the host has been used without being rebooted
    Local:
        locked_by: user that locked the host, or null if the host is unlocked
    """

    __tablename__ = "afe_hosts"

    SERIALIZATION_LINKS_TO_FOLLOW = {
        "aclgroup_set",
        "hostattribute_set",
        "labels",
        "shard",
    }
    SERIALIZATION_LOCAL_LINKS_TO_UPDATE = {"invalid"}

    id = Column(Integer, primary_key=True)
    hostname = Column(String(length=255), unique=True)
    locked = Column(Boolean, default=False)
    synch_id = Column(Integer, default=None)
    status = Column(String(length=255), default=None)
    invalid = Column(Boolean, default=False)
    protection = Column(Integer, nullable=False)
    locked_by_id = Column(Integer, default=None)
    lock_time = Column(DateTime, default=None)
    dirty = Column(Boolean, default=False)
    leased = Column(Boolean, nullable=False, default=True)
    shard_id = Column(Integer, default=None)
    lock_reason = Column(Text, default=None)
