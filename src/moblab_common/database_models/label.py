# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class Label(declarative_base()):
    """
    Required:
      name: label name

    Optional:
      kernel_config: URL/path to kernel config for jobs run on this label.
      platform: If True, this is a platform label (defaults to False).
      only_if_needed: If True, a Host with this label can only be used if that
              label is requested by the job/test (either as the meta_host or
              in the job_dependencies).
      atomic_group: The atomic group associated with this label.
    """

    __tablename__ = "afe_labels"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), unique=True)
    kernel_config = Column(String(length=255), default=None)
    platform = Column(Boolean, default=False)
    invalid = Column(Boolean, default=False)
    only_if_needed = Column(Boolean, default=False)
    atomic_group_id = Column(Integer, nullable=True, default=None)
