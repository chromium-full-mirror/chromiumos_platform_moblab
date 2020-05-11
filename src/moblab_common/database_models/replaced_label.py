# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base


class ReplacedLabel(declarative_base()):
    """The tag to indicate Whether to replace labels with static labels."""
    __tablename__ = 'afe_replaced_labels'

    id = Column(Integer, primary_key=True)
    label_id = Column(Integer, default=None, unique=True)
