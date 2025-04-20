import sqlmodel

import models


def create(db_session: sqlmodel.Session, name: str, service: str, state: str) -> models.Daemon:
    daemon = models.Daemon(
        name=name,
        service=service,
        state=state,
    )

    db_session.add(daemon)
    db_session.commit()

    return daemon
