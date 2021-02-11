# -*- coding: utf-8 -*-
# Copyright 2020 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import logging
import enum
from datetime import datetime

from moblab_common.database_models.job_uploading_status import (
    JobUploadingStatus,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Status = enum.Enum(
    "Status",
    [
        "NOT_READY",
        "QUEUED",
        "UPLOADING",
        "UPLOADED",
        "UPLOAD_FAILED",
        "DELETED",
    ],
)


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
    """Represents the known info about upload status"""

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
        upload_status = {job_id: UploadResultState() for job_id in job_id_list}
        if job_id_list:
            session = self.db.get_session()
            results = (
                session.query(JobUploadingStatus)
                .filter(JobUploadingStatus.job_id.in_(job_id_list))
                .all()
            )
            session.close()
            for r in results:
                state = upload_status[r.job_id]
                state.status = Status[r.status].name
                state.attempt_number = r.upload_attempt_number
                state.last_falure_reason = r.last_attempt_failure_reason

        return upload_status

    def set_job_upload_status(self, job_id, status, failure_reason=""):
        """Updates the upload status for a given job"""
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
                        status=status,
                        upload_attempt_number=1,
                        updated_on=datetime.now(datetime.timezone.utc),
                    )
                )
            else:
                logging.info(
                    'Updating job "%s" upload status "%s" -> "%s"',
                    job_id,
                    upload_status.status,
                    status,
                )
                upload_status.status = status
                upload_status.upload_attempt_number = (
                    upload_status.upload_attempt_number + 1
                )
                if status == Status.UPLOAD_FAILED.name:
                    upload_status.last_attempt_failure_reason = failure_reason
                    upload_status.updated_on = datetime.now(
                        datetime.timezone.utc
                    )

            session.commit()
        finally:
            session.close()
