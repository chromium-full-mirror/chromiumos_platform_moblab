# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class StaticLabel(declarative_base()):
    """
    Required:
      name: label name

    Optional:
      kernel_config: URL/path to kernel config for jobs run on this label.
      platform: If True, this is a platform label (defaults to False).
      only_if_needed: Deprecated. This is always False.
      atomic_group: Deprecated. This is always NULL.
    """
    __tablename__ = 'afe_static_labels'
    name_field = 'name'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), unique=True)
    kernel_config = Column(String(length=255), default=None)
    platform = Column(Boolean, default=False)
    invalid = Column(Boolean, default=False)
    only_if_needed = Column(Boolean, default=False)
    atomic_group_id = Column(Integer, nullable=True, default=None)
