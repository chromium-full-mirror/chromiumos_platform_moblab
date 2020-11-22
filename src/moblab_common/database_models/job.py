# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    SmallInteger,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base

from database_models.common.constants import Constants


class Job(declarative_base()):
    """
    owner: username of job owner
    name: job name (does not have to be unique)
    priority: Integer priority value.  Higher is more important.
    control_file: contents of control file
    control_type: Client or Server
    created_on: date of job creation
    submitted_on: date of job submission
    synch_count: how many hosts should be used per autoserv execution
    run_verify: Whether or not to run the verify phase
    run_reset: Whether or not to run the reset phase
    timeout: DEPRECATED - hours from queuing time until job times out
    timeout_mins: minutes from job queuing time until the job times out
    max_runtime_hrs: DEPRECATED - hours from job starting time until job
                     times out
    max_runtime_mins: minutes from job starting time until job times out
    email_list: list of people to email on completion delimited by any of:
                white space, ',', ':', ';'
    dependency_labels: many-to-many relationship with labels corresponding to
                       job dependencies
    reboot_before: Never, If dirty, or Always
    reboot_after: Never, If all tests passed, or Always
    parse_failed_repair: if True, a failed repair launched by this job will have
    its results parsed as part of the job.
    drone_set: The set of drones to run this job on
    parent_job: Parent job (optional)
    test_retry: Number of times to retry test if the test did not complete
                successfully. (optional, default: 0)
    require_ssp: Require server-side packaging unless require_ssp is set to
                 False. (optional, default: None)
    """

    __tablename__ = "afe_jobs"

    # TODO: Investigate, if jobkeyval_set is really needed.
    # dynamic_suite will write them into an attached file for the drone, but
    # it doesn't seem like they are actually used. If they aren't used, remove
    # jobkeyval_set here.
    SERIALIZATION_LINKS_TO_FOLLOW = {
        "dependency_labels",
        "hostqueueentry_set",
        "jobkeyval_set",
        "shard",
    }

    EXCLUDE_KNOWN_JOBS_CLAUSE = """
        AND NOT (afe_host_queue_entries.aborted = 0
                 AND afe_jobs.id IN (%(known_ids)s))
    """

    EXCLUDE_OLD_JOBS_CLAUSE = 'AND (afe_jobs.created_on > "%(cutoff)s")'

    SQL_SHARD_JOBS = """
        SELECT DISTINCT(afe_jobs.id) FROM afe_jobs
        INNER JOIN afe_host_queue_entries
          ON (afe_jobs.id = afe_host_queue_entries.job_id)
        LEFT OUTER JOIN afe_jobs_dependency_labels
          ON (afe_jobs.id = afe_jobs_dependency_labels.job_id)
        JOIN afe_shards_labels
          ON (afe_shards_labels.label_id = afe_jobs_dependency_labels.label_id
              OR afe_shards_labels.label_id = afe_host_queue_entries.meta_host)
        WHERE (afe_shards_labels.shard_id = %(shard_id)s
               AND afe_host_queue_entries.complete != 1
               AND afe_host_queue_entries.active != 1
               %(exclude_known_jobs)s
               %(exclude_old_jobs)s)
    """

    # Jobs can be created with assigned hosts and have no dependency
    # labels nor meta_host.
    # We are looking for:
    #     - a job whose hqe's meta_host is null
    #     - a job whose hqe has a host
    #     - one of the host's labels matches the shard's label.
    # Non-aborted known jobs, completed jobs, active jobs, jobs
    # without hqe are exluded as we do with SQL_SHARD_JOBS.
    SQL_SHARD_JOBS_WITH_HOSTS = """
        SELECT DISTINCT(afe_jobs.id) FROM afe_jobs
        INNER JOIN afe_host_queue_entries
          ON (afe_jobs.id = afe_host_queue_entries.job_id)
        LEFT OUTER JOIN %(host_label_table)s
          ON (afe_host_queue_entries.host_id = %(host_label_table)s.host_id)
        WHERE (%(host_label_table)s.%(host_label_column)s IN %(label_ids)s
               AND afe_host_queue_entries.complete != 1
               AND afe_host_queue_entries.active != 1
               AND afe_host_queue_entries.meta_host IS NULL
               AND afe_host_queue_entries.host_id IS NOT NULL
               %(exclude_known_jobs)s
               %(exclude_old_jobs)s)
    """

    # Even if we had filters about complete, active and aborted
    # bits in the above two SQLs, there is a chance that
    # the result may still contain a job with an hqe with 'complete=1'
    # or 'active=1'.'
    # This happens when a job has two (or more) hqes and at least
    # one hqe has different bits than others.
    # We use a second sql to ensure we exclude all un-desired jobs.
    SQL_JOBS_TO_EXCLUDE = """
        SELECT afe_jobs.id FROM afe_jobs
        INNER JOIN afe_host_queue_entries
          ON (afe_jobs.id = afe_host_queue_entries.job_id)
        WHERE (afe_jobs.id in (%(candidates)s)
               AND (afe_host_queue_entries.complete=1
                    OR afe_host_queue_entries.active=1))
    """

    RebootBefore = Constants.REBOOT_BEFORE
    RebootAfter = Constants.REBOOT_AFTER

    id = Column(Integer, primary_key=True)
    owner = Column(String(length=255), default=None)
    name = Column(String(length=255), default=None)
    priority = Column(Integer, default=None)
    control_file = Column(Text, default=None)
    control_type = Column(Integer, default=None)
    created_on = Column(DateTime, default=None)
    synch_count = Column(Integer, nullable=False, default=0)
    # TODO: Config the default values by migrating the global_config class.
    timeout = Column(Integer, nullable=False)
    run_verify = Column(Boolean, default=True)
    email_list = Column(String(length=250), nullable=False)
    reboot_before = Column(SmallInteger, nullable=False)
    reboot_after = Column(SmallInteger, nullable=False, default=1)
    parse_failed_repair = Column(Boolean, nullable=False, default=1)
    max_runtime_hrs = Column(Integer, nullable=False)
    max_runtime_mins = Column(Integer, nullable=False)
    drone_set_id = Column(Integer, default=None)
    parameterized_job_id = Column(Integer, default=None)
    parent_job_id = Column(Integer, default=None)
    test_retry = Column(Integer, nullable=False, default=0)
    run_reset = Column(SmallInteger, nullable=False, default=1)
    timeout_mins = Column(Integer, nullable=False)
    shard_id = Column(Integer, default=None)
    require_ssp = Column(Boolean, default=None)
