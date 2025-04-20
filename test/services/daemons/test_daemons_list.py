import sqlmodel

import models
import services.daemons


def test_daemon_create(db_session: sqlmodel.Session):
    daemon = services.daemons.create(
        db_session=db_session,
        name="test-1",
        service="workq-0",
        state=models.daemon.STATE_RUNNING,
    )

    assert daemon.id

    # should find all daemons

    list_result = services.daemons.list(
        db_session=db_session,
        query="",
        offset=0,
        limit=10,
    )

    assert list_result.code == 0
    assert list_result.count == 1
    assert list_result.total == 1
    assert list_result.objects == [daemon]

    # should find daemon with name match

    list_result = services.daemons.list(
        db_session=db_session,
        query="name:test-1",
        offset=0,
        limit=10,
    )

    assert list_result.code == 0
    assert list_result.count == 1
    assert list_result.total == 1
    assert list_result.objects == [daemon]

    # should find daemon with state match

    list_result = services.daemons.list(
        db_session=db_session,
        query="state:running",
        offset=0,
        limit=10,
    )

    assert list_result.code == 0
    assert list_result.count == 1
    assert list_result.total == 1
    assert list_result.objects == [daemon]

    # should find no daemons with no name match

    list_result = services.daemons.list(
        db_session=db_session,
        query="name:foo",
        offset=0,
        limit=10,
    )

    assert list_result.code == 0
    assert list_result.count == 0
    assert list_result.total == 0
    assert list_result.objects == []

    db_session.delete(daemon)
    db_session.commit()
