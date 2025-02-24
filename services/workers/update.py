import sqlmodel

import models
import services.workers


def state_busy(db_session: sqlmodel.Session, name: str) -> int:
    _state_update(db_session=db_session, name=name, state=models.worker.STATE_BUSY)


def state_idle(db_session: sqlmodel.Session, name: str) -> int:
    _state_update(db_session=db_session, name=name, state=models.worker.STATE_IDLE)


def state_term(db_session: sqlmodel.Session, name: str) -> int:
    _state_update(db_session=db_session, name=name, state=models.worker.STATE_TERM)


def _state_update(db_session: sqlmodel.Session, name: str, state: str) -> int:
    worker = services.workers.get_by_name(db_session, name=name)

    if not worker:
        return 404

    worker.state = state

    db_session.add(worker)
    db_session.commit()

    return 0
