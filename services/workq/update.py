import datetime

import sqlmodel

import models


def state_completed(db_session: sqlmodel.Session, workq: models.WorkQ) -> int:
    """
    Mark work object as completed
    """
    if workq.state == models.workq.STATE_COMPLETED:
        return 409

    workq.state = models.workq.STATE_COMPLETED
    workq.completed_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(workq)
    db_session.commit()

    return 0


def state_error(db_session: sqlmodel.Session, workq: models.WorkQ) -> int:
    """
    Mark work object as error
    """
    if workq.state == models.workq.STATE_ERROR:
        return 409

    workq.state = models.workq.STATE_ERROR
    workq.completed_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(workq)
    db_session.commit()

    return 0


def state_processing(db_session: sqlmodel.Session, workq: models.WorkQ, worker: str) -> int:
    """
    Mark work object as processing
    """
    if workq.state == models.workq.STATE_PROCESSING:
        return 409

    workq.state = models.workq.STATE_PROCESSING
    workq.processing_at = datetime.datetime.now(datetime.timezone.utc)
    workq.worker = worker

    db_session.add(workq)
    db_session.commit()

    return 0