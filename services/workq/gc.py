import sqlmodel

import models
import services.mql
import services.workq


def gc(db_session: sqlmodel.Session, queue: str, completed_before: int) -> int:
    """
    Garbage collect work queue objects completed before completed_before
    """
    workq_objects = services.workq.list(
        db_session=db_session,
        query=f"name:{queue} state:{models.workq.STATE_COMPLETED} completed_at:<{completed_before}",
        limit=1024,
        offset=0,
    )

    deleted = 0

    for workq in workq_objects:
        db_session.delete(workq)
        db_session.commit()

        deleted += 1

    return deleted