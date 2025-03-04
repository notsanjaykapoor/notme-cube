import sqlmodel

import models
import services.clusters
import services.clusters.requests
import services.database

def test_request_add(db_session: sqlmodel.Session, cluster_1: models.Cluster):
    assert cluster_1.state == "running"

    request_result = services.clusters.requests.add(
        db_session=db_session,
        cluster_id=cluster_1.id,
        cluster_ask=2,
        data={
            "machine_name": "machine-1"
        }
    )

    cluster_request = request_result.object

    assert request_result.code == 0
    assert cluster_request.created_at
    assert cluster_request.data == {"machine_name": "machine-1"}
    assert cluster_request.id == cluster_1.id
    assert cluster_request.machine_name == "machine-1"
    assert cluster_request.size_ask == 2
    assert cluster_request.size_has == cluster_1.size_has
    assert cluster_request.state == "queued"

    # cluster state should be updated

    cluster = services.clusters.get_by_id(db_session=db_session, id=cluster_1.id)

    assert cluster.size_ask == 2
    assert cluster.state == "scaling"

    # not allowed to add requests if there are pending requests

    request_result = services.clusters.requests.add(
        db_session=db_session,
        cluster_id=cluster_1.id,
        cluster_ask=2,
    )

    assert request_result.code == 422
    assert request_result.object == None

    # not valid to add requests with invalid cluster id

    request_result = services.clusters.requests.add(
        db_session=db_session,
        cluster_id=0,
        cluster_ask=2,
    )

    assert request_result.code == 422
    assert request_result.object == None

    # get pending request

    get_result = services.clusters.requests.get_pending_by_cluster(
        db_session=db_session,
        cluster_id=cluster_1.id,
    )

    assert get_result == cluster_request

    db_session.delete(cluster_request)
    db_session.commit()
