import dataclasses

import sqlmodel

import models
import services.clusters
import services.clusters.requests
import services.machines

@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


def process(db_session: sqlmodel.Session, request: models.ClusterRequest) -> Struct:
    """
    """
    struct = Struct(
        code=0,
        errors=[],
    )

    cluster = services.clusters.get_by_id(
        db_session=db_session,
        id=request.cluster_id,
    )

    if request.state == models.cluster_request.STATE_QUEUED:
        if cluster.state != models.cluster.STATE_SCALING:
            # invalid state, the request should have changed the cluster state
            raise Exception(f"cluster state '{cluster.state}' invalid")

        request.state = models.cluster_request.STATE_PROCESSING

        db_session.add(request)
        db_session.commit()

    if cluster.size_has == cluster.size_ask:
        # request completed
        cluster.state = models.cluster.STATE_RUNNING
        request.state = models.cluster_request.STATE_COMPLETED

        db_session.add(cluster)
        db_session.add(request)
        db_session.commit()
    elif cluster.size_has < cluster.size_ask:
        machine_tags = {}

        if models.service.SERVICE_WORKQ in cluster.services_list:
            machine_tags["services"] = models.service.SERVICE_WORKQ_WORKER

        code, _machine = services.clusters.requests.machine_add(
            cluster=cluster,
            machine_tags=machine_tags,
        )

        if code != 0:
            # todo
            request.state = models.cluster_request.STATE_ERROR
            db_session.add(request)
            db_session.commit()
            struct.code = 500
            return struct

        cluster.size_has += 1
        db_session.add(cluster)
        db_session.commit()
    else:
        code = services.clusters.requests.machine_remove(
            cluster=cluster,
            machine_name=request.machine_name,
        )

        if code != 0:
            # todo
            request.state = models.cluster_request.STATE_ERROR
            db_session.add(request)
            db_session.commit()
            struct.code = 500
            return struct

        cluster.size_has -= 1
        db_session.add(cluster)
        db_session.commit()

    return struct

