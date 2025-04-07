import dataclasses
import datetime
import pytz

import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    active: list[models.Worker]
    exited: list[models.Worker]
    errors: list[str]


def active_check(db_session: sqlmodel.Session, workers: list[str], seconds: int) -> Struct:
    """
    Check worker database objects and partition into active and exited lists based on its updated_at timestamp.
    """
    struct = Struct(
        code=0,
        active=[],
        exited=[],
        errors=[],
    )

    workers = db_session.exec(
        sqlmodel
            .select(models.Worker)
            .where(models.Worker.name.in_(workers))
    ).all()

    for worker in workers:
        diff_seconds = datetime.datetime.now(datetime.timezone.utc).timestamp() - worker.updated_at.replace(tzinfo=pytz.utc).timestamp()

        if diff_seconds > seconds:
            struct.exited.append(worker)
        else:
            struct.active.append(worker)

    return struct


def state_check(db_session: sqlmodel.Session, seconds: int) -> Struct:
    """
    Check worker database objects and partition into active and stale lists based on its updated_at timestamp.
    """
    struct = Struct(
        code=0,
        active=[],
        exited=[],
        errors=[],
    )
    workers = db_session.exec(
        sqlmodel
            .select(models.Worker)
            .where(models.Worker.state != models.worker.STATE_TERM)
    ).all()

    for worker in workers:
        diff_seconds = datetime.datetime.now(datetime.timezone.utc).timestamp() - worker.updated_at.replace(tzinfo=pytz.utc).timestamp()

        if diff_seconds > seconds:
            struct.exited.append(worker)
        else:
            struct.active.append(worker)

    return struct