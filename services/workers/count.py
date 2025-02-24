import sqlalchemy
import sqlmodel

import models


def count_active(db_session: sqlmodel.Session) -> int:
    """
    get count of workers that are not terminated
    """
    return db_session.scalar(
        sqlmodel.select(
            sqlalchemy.func.count(models.Worker.id)
        ).where(models.Worker.state.in_(models.worker.STATES_ACTIVE))
    )


def count_all(db_session: sqlmodel.Session) -> int:
    """
    get count of all workers independent of state
    """
    return db_session.scalar(
        sqlmodel.select(
            sqlalchemy.func.count(models.Worker.id)
        )
    )
