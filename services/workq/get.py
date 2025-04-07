import sqlmodel

import models


def get_by_id(db_session: sqlmodel.Session, id: int) -> models.WorkQ | None:
    return db_session.exec(
        sqlmodel
            .select(models.WorkQ)
            .where(models.WorkQ.id == id)
    ).first()


def get_processing_all(db_session: sqlmodel.Session) -> list[models.WorkQ]:
    return db_session.exec(
        sqlmodel
            .select(models.WorkQ)
            .where(models.WorkQ.state == models.workq.STATE_PROCESSING)
    ).all()


def get_processing_by_worker_id(db_session: sqlmodel.Session, worker_id: str) -> list[models.WorkQ]:
    return db_session.exec(
        sqlmodel
            .select(models.WorkQ)
            .where(models.WorkQ.state == models.workq.STATE_PROCESSING)
            .where(models.WorkQ.worker == worker_id)
    ).all()


def get_queued(db_session: sqlmodel.Session, queue: str, partition: int) -> models.WorkQ | None:
    """
    Get the next work queue object for the specified queue and partition
    """
    model = models.WorkQ

    return db_session.exec(
        sqlmodel
            .select(model)
            .where(model.name == queue).where(model.partition == partition).where(model.state == models.workq.STATE_QUEUED)
            .order_by(model.id.asc())
    ).first()
