# -*- coding: utf-8 -*-
# Copyright 2021 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import logging
import enum
from datetime import datetime
from datetime import timezone

from moblab_common.database_models.job_uploading_status import (
    JobUploadingStatus,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Status(enum.Enum):
    NOT_READY = 1
    QUEUED = 2
    UPLOADING = 3
    UPLOADED = 4
    UPLOAD_FAILED = 5
    DELETED = 6


# ToDo(ivanbrovkovich): decide on DB access location
class MoblabDb:
    # ToDo(ivanbrovkovich): push configuration to env vars
    _engine = create_engine(
        "mysql+pymysql://root:moblab_db_passwd@db:3306/moblab",
        pool_pre_ping=True,
    )
    _Session = sessionmaker(bind=_engine)

    def get_session(self):
        return MoblabDb._Session()


class UploadResultState:
    """Represents the known info about job upload status"""

    def __init__(
        self,
        status=Status.NOT_READY.name,
        attempt_number=0,
        last_falure_reason="",
    ):
        self.status = status
        self.attempt_number = attempt_number
        self.last_falure_reason = last_falure_reason


class ResultUploadStatusConnector:
    """Abstraction around persistence layer for uploading status by result"""

    def __init__(self):
        self.db = MoblabDb()

    def get_jobs_upload_status(self, job_id_list):
        """Returns the list of upload statuses for requested jobs"""
        upload_status = {}
        if job_id_list:
            session = self.db.get_session()
            results = (
                session.query(JobUploadingStatus)
                .filter(JobUploadingStatus.job_id.in_(job_id_list))
                .all()
            )
            session.close()
            for r in results:
                state = UploadResultState()
                state.status = Status[r.status].name
                state.attempt_number = r.upload_attempt_number
                state.last_falure_reason = r.last_attempt_failure_reason
                upload_status[r.job_id] = state

        return upload_status

    def set_job_upload_status(self, job_id, status, failure_reason=""):
        """Updates the upload status for a given job
        Args:
            job_id: (int) job id value
            status: (Status) enum value
            failure_reason: (string) error message in case of failure attempt
        """
        session = self.db.get_session()
        try:
            upload_status = (
                session.query(JobUploadingStatus)
                .filter_by(job_id=job_id)
                .first()
            )
            if not upload_status:
                logging.info(
                    'Insert job "%s" upload status "%s"',
                    job_id,
                    status,
                )
                session.add(
                    JobUploadingStatus(
                        job_id=job_id,
                        status=status.name,
                        upload_attempt_number=(
                            1 if status == Status.UPLOAD_FAILED else 0
                        ),
                        updated_on=datetime.now(timezone.utc),
                    )
                )
            else:
                logging.info(
                    'Updating job "%s" upload status "%s" -> "%s"',
                    job_id,
                    upload_status.status,
                    status,
                )
                upload_status.status = status.name
                upload_status.upload_attempt_number = (
                    upload_status.upload_attempt_number
                    + (1 if status == Status.UPLOAD_FAILED else 0)
                )
                if status == Status.UPLOAD_FAILED:
                    upload_status.last_attempt_failure_reason = failure_reason
                    upload_status.updated_on = datetime.now(timezone.utc)

            session.commit()
        finally:
            session.close()
