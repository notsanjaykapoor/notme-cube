import sqlalchemy
import sqlmodel

import models


def count_queued(db_session: sqlmodel.Session, queue: str) -> int:
    """
    get count of workq objects in 'queued' state
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
