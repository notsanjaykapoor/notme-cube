import sqlmodel

import models
import services.workq

def cleanup(db_session: sqlmodel.Session, queue: str, partition: int) -> int:
    """
    Reset all processing work objects as queued.

    Work objects can be left in a processing state during shutdown.
    """
    updated_count = 0

    list_result = services.workq.list(
        db_session=db_session,
        query=f"name:{queue} partition:{partition} state:{models.workq.STATE_PROCESSING}",
        offset=0,
        limit=10,
    )

    for workq in list_result.objects:
        workq.state = models.workq.STATE_QUEUED
        workq.processing_at = None

        db_session.add(workq)
        db_session.commit()

        updated_count += 1

    return updated_count