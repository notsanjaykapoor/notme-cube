import pytest

import sqlmodel
import sqlalchemy.exc

import models
import services.daemons


def test_daemon_create(db_session: sqlmodel.Session):
    daemon_1 = services.daemons.create(
        db_session=db_session,
        name="test-1",
        service="workq-0",
        state=models.daemon.STATE_RUNNING,
    )

    assert daemon_1.id

    daemon_2 = services.daemons.get_by_name_service(
        db_session=db_session,
        name="test-1",
        service="workq-0",
    )

    assert daemon_2.id == daemon_1.id

    # daemon [name, service] is unique

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        services.daemons.create(
            db_session=db_session,
            name="test-1",
            service="workq-0",
            state=models.daemon.STATE_SHUTDOWN,
        )

    db_session.rollback()

    db_session.delete(daemon_1)
    db_session.delete(daemon_2)
    db_session.commit()
