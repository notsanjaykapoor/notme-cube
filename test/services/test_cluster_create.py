import pytest

import sqlmodel
import sqlalchemy.exc

import services.clusters


def test_cluster_create(db_session: sqlmodel.Session):
    cluster = services.clusters.create(
        db_session=db_session,
        name="test",
    )

    assert cluster.id
    assert cluster.cloud == "hetzner"
    assert cluster.data == {"cloud": "hetzner", "server_image": "ubuntu-24.04", "server_location": "ash", "server_type": "cpx11"}
    assert cluster.name == "test"
    assert cluster.server_image == "ubuntu-24.04"
    assert cluster.server_location == "ash"
    assert cluster.server_type == "cpx11"
    assert cluster.size_ask == 0
    assert cluster.size_has == 0
    assert cluster.state == "active"

    # cluster name is unique

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        services.clusters.create(
            db_session=db_session,
            name="test",
        )

    db_session.rollback()

    db_session.delete(cluster)
    db_session.commit()


