import sqlmodel

import models


def get_by_name(db_session: sqlmodel.Session, name: str) -> models.Worker | None:
    worker = db_session.exec(
        sqlmodel
            .select(models.Worker)
            .where(models.Worker.name == name)
    ).first()

    return worker
