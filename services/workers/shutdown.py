import sqlmodel

import models
import services.database
import services.workq


def shutdown(db_session: sqlmodel.Session, queue: str, sender: str, worker_name: str) -> int:
    """
    Add shutdown message to the workq requesting the specified worker to shutdown.
    """
    services.workq.add(
        db_session=db_session,
        queue=queue,
        partition=-1,
        msg=models.workq.MSG_SHUTDOWN,
        data={
            "sender": sender,
            "worker_name": worker_name,
        })
    
    return 0
