import sqlalchemy
import sqlmodel

import models


def count(db_session: sqlmodel.Session) -> int:
    """
    get workers count
    """
    return db_session.scalar(
        sqlmodel.select(
            sqlalchemy.func.count(models.Worker.id)
        )
    )
