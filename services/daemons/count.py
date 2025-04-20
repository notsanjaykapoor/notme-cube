import sqlalchemy
import sqlmodel

import models


def count_active(db_session: sqlmodel.Session) -> int:
    """
    get count of daemons that are in the "active" virtual state
    """
    return db_session.scalar(
        sqlmodel.select(
            sqlalchemy.func.count(models.Daemon.id)
        ).where(models.Daemon.state.in_(models.daemon.STATES_ACTIVE))
    )


def count_all(db_session: sqlmodel.Session) -> int:
    """
    get count of all daemons independent of state
    """
    return db_session.scalar(
        sqlmodel.select(
            sqlalchemy.func.count(models.Daemon.id)
        )
    )
