import datetime

import sqlmodel

import models
import services.workers


def get_by_name(db_session: sqlmodel.Session, name: str) -> models.Worker | None:
    worker = db_session.exec(
        sqlmodel
            .select(models.Worker)
            .where(models.Worker.name == name)
    ).first()

    return worker


def get_or_create(db_session: sqlmodel.Session, name: str, state: str) -> tuple[int, models.Worker]:
    """
    Find existing worker or create new worker, and update worker state
    """
    worker = get_by_name(db_session=db_session, name=name)

    if worker:
        code = 0
    else:
        worker = services.workers.create(db_session=db_session, name=name)
        code = 201

    worker.state = state
    worker.updated_at = datetime.datetime.now(datetime.timezone.utc)

    db_session.add(worker)
    db_session.commit()

    return [code, worker]

