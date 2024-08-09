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


def get_or_create(db_session: sqlmodel.Session, name: str, state: str) -> models.Worker:
    """
    Find existing worker or create new worker, and update worker state
    """
    worker = get_by_name(db_session=db_session, name=name)
    worker = worker or services.workers.create(db_session=db_session, name=name)

    if worker.state != state:
        worker.state = state

        db_session.add(worker)
        db_session.commit()

    return worker

