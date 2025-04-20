import sqlmodel

import models


def get_by_name_service(db_session: sqlmodel.Session, name: str, service: str) -> models.Daemon | None:
    daemon = db_session.exec(
        sqlmodel
            .select(models.Daemon)
            .where(models.Daemon.name == name)
            .where(models.Daemon.service == service)
    ).first()

    return daemon

