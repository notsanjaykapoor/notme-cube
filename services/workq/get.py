import sqlmodel

import models


def get_by_id(db_session: sqlmodel.Session, id: int) -> models.WorkQ | None:
    workq = db_session.exec(
        sqlmodel
            .select(models.WorkQ)
            .where(models.WorkQ.id == id)
    ).first()

    return workq


def get_queued(db_session: sqlmodel.Session, queue: str, partition: int) -> models.WorkQ | None:
    """
    Get the next work queue object for the specified queue and partition
    """
    model = models.WorkQ

    workq = db_session.exec(
        sqlmodel
            .select(model)
            .where(model.name == queue).where(model.partition == partition).where(model.state == models.workq.STATE_QUEUED)
            .order_by(model.id.asc())
    ).first()

    return workq
