# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


class AtomicGroup(declarative_base()):
    """
    An atomic group defines a collection of hosts which must only be scheduled
    all at once.  Any host with a label having an atomic group will only be
    scheduled for a job at the same time as other hosts sharing that label.

    Required:
      name: A name for this atomic group, e.g. 'rack23' or 'funky_net'.
      max_number_of_machines: The maximum number of machines that will be
              scheduled at once when scheduling jobs to this atomic group.
              The job.synch_count is considered the minimum.

    Optional:
      description: Arbitrary text description of this group's purpose.
    """

    __tablename__ = "afe_atomic_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), unique=True)
    description = Column(Text, default=None)
    # This magic value is the default to simplify the scheduler logic.
    # It must be "large".  The common use of atomic groups is to want all
    # machines in the group to be used, limits on which subset used are
    # often chosen via dependency labels.
    # TODO(dennisjeffrey): Revisit this so we don't have to assume that
    # "infinity" is around 3.3 million.
    INFINITE_MACHINES = 333333333
    max_number_of_machines = Column(Integer, default=INFINITE_MACHINES)
    invalid = Column(Boolean, default=False)
