import sqlmodel

import models


def remove(db_session: sqlmodel.Session, id: int,) -> int:
    workq = db_session.exec(
        sqlmodel.select(models.WorkQ).where(models.WorkQ.id == id)
    ).first()

    if not workq:
        return 404

    db_session.delete(workq)
    db_session.commit()

    return 0