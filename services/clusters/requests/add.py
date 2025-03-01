import dataclasses

import sqlmodel

import models
import services.clusters.requests

@dataclasses.dataclass
class Struct:
    code: int
    object: models.ClusterRequest
    errors: list[str]


def add(db_session: sqlmodel.Session, cluster_id: int, cluster_ask: int, data: dict={}) -> Struct:
    """
    Add cluster request to database.
    """
    struct = Struct(
        code=0,
        object=None,
        errors=[],
    )

    list_result = services.clusters.requests.list(
        db_session=db_session,
        query=f"state:{models.cluster_request.STATE_PENDING} cluster_id:{cluster_id}",
        offset=0,
        limit=1,
    )

    if list_result.total > 0:
        struct.code = 422
        return struct

    cluster = services.clusters.get_by_id(db_session=db_session, id=cluster_id)

    if not cluster:
        struct.code = 422
        return struct

    if cluster.state != models.cluster.STATE_RUNNING:
        struct.code = 422
        return struct

    struct.object = models.ClusterRequest(
        cluster_id=cluster.id,
        data=data,
        size_ask=cluster_ask + cluster.size_has,
        size_has=cluster.size_has,
        state=models.cluster_request.STATE_QUEUED,
    )

    cluster.size_ask = struct.object.size_ask
    cluster.state = models.cluster.STATE_SCALING

    db_session.add(cluster)
    db_session.add(struct.object)
    db_session.commit()

    return struct