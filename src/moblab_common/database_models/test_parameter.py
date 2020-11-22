# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class TestParameter(declarative_base()):
    """
    A declared parameter of a test
    """

    __tablename__ = "afe_test_parameters"

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, nullable=False)
    name = Column(String(length=255), nullable=False)
