import sqlmodel

import models


def create(db_session: sqlmodel.Session, name: str) -> models.Worker:
    worker = models.Worker(
        name=name,
    )

    db_session.add(worker)
    db_session.commit()

    return worker
