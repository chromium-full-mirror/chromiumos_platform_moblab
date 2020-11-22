# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class AclGroup(declarative_base()):
    """
    Required:
    name: name of ACL group

    Optional:
    description: arbitrary description of group
    """

    __tablename__ = "afe_acl_groups"

    name_field = "name"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), default=None)
    description = Column(String(length=255), default=None)
