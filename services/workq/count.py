import sqlalchemy
import sqlmodel

import models


def count_queued(db_session: sqlmodel.Session, queue: str) -> int:
    """
    get count of workq objects in 'queued' state in the specified queue
    """
    return db_session.scalar(
        sqlmodel.select(
            sqlalchemy.func.count(models.WorkQ.id)
        ).where(
            models.WorkQ.name == queue
        ).where(
            models.WorkQ.state == models.workq.STATE_QUEUED
        )
    )


def count_queued_all(db_session: sqlmodel.Session) -> int:
    """
    get count of workq objects in 'queued' state in any queue
    """
    return db_session.scalar(
        sqlmodel.select(
            sqlalchemy.func.count(models.WorkQ.id)
        ).where(
            models.WorkQ.state == models.workq.STATE_QUEUED
        )
    )
