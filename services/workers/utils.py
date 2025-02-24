import dataclasses
import datetime
import pytz

import sqlmodel

import models


THRESHOLD_SECONDS = 60

@dataclasses.dataclass
class Struct:
    code: int
    active: list[models.Worker]
    stale: list[models.Worker]
    errors: list[str]



def state_check(db_session: sqlmodel.Session) -> Struct:
    """
    Check worker database objects and partition into active and stale lists based on its updated_at timestamp.
    """
    struct = Struct(
        code=0,
        active=[],
        stale=[],
        errors=[],
    )
    workers = db_session.exec(
        sqlmodel
            .select(models.Worker)
            .where(models.Worker.state != models.worker.STATE_TERM)
    ).all()

    for worker in workers:
        seconds = datetime.datetime.now(datetime.timezone.utc).timestamp() - worker.updated_at.replace(tzinfo=pytz.utc).timestamp()

        if seconds > THRESHOLD_SECONDS:
            struct.stale.append(worker)
        else:
            struct.active.append(worker)

    return struct