import datetime

import sqlmodel

import models


def state_completed(db_session: sqlmodel.Session, job: models.WorkQ) -> int:
    """
    Mark job state as completed and set completed_at timestamp.
    """
    if job.state == models.workq.STATE_COMPLETED:
        return 409

    job.state = models.workq.STATE_COMPLETED
    job.completed_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(job)
    db_session.commit()

    return 0


def state_error(db_session: sqlmodel.Session, job: models.WorkQ) -> int:
    """
    Mark job state as error and set completed_at timestamp.
    """
    if job.state == models.workq.STATE_ERROR:
        return 409

    job.state = models.workq.STATE_ERROR
    job.completed_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(job)
    db_session.commit()

    return 0


def state_processing(db_session: sqlmodel.Session, job: models.WorkQ, worker: str) -> int:
    """
    Mark job state as processing and set processing_at timestamp.
    """
    if job.state == models.workq.STATE_PROCESSING:
        return 409

    job.state = models.workq.STATE_PROCESSING
    job.processing_at = datetime.datetime.now(datetime.timezone.utc)
    job.worker = worker

    db_session.add(job)
    db_session.commit()

    return 0