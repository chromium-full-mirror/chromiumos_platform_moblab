# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class DroneSet(declarative_base()):
    """
    A set of scheduler drones

    These will be used by the scheduler to decide what drones a job is allowed
    to run on.

    name: the drone set's name
    drones: the drones that are part of the set
    """

    __tablename__ = "afe_drone_sets"
    name_field = "name"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), unique=True)
