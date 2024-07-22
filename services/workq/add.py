import sqlmodel

import models


def add(db_session: sqlmodel.Session, queue: str, partition: int, msg: str, data: dict) -> int:
    workq = models.WorkQ(
        data=data,
        msg=msg,
        name=queue,
        partition=partition,
        state=models.workq.STATE_QUEUED,
    )

    try:
        db_session.add(workq)
        db_session.commit()
    except Exception:
        db_session.rollback()
        return 422

    return 0