import dataclasses

import sqlmodel

import models
import services.clusters
import services.clusters.requests
import services.hetzner.servers
import services.hetzner.ssh_keys
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
            raise Exception("cluster state invalid")

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
        code = _machine_add(cluster=cluster)

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
        code = _machine_remove(cluster=cluster, machine_name=request.machine_name)

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


def _machine_add(cluster: models.Cluster) -> int:
    """
    Add machine to cluster.
    """
    list_result = services.machines.list(cluster=cluster)
    machines_list = list_result.objects_list

    # generate new machine name
    machine_names = [machine.name for machine in machines_list]
    machine_name = services.clusters.machine_name_generate(cluster=cluster, names=machine_names)

    # get primary ssh key
    ssh_keys_struct = services.hetzner.ssh_keys.list()
    ssh_key_name = ssh_keys_struct.objects[0].name

    # generate machine tag
    machine_tags = {
        "cluster": cluster.name,
    }

    # add machine to cluster
    create_result = services.hetzner.servers.create(
        cluster=cluster,
        name=machine_name,
        ssh_key=ssh_key_name,
        tags=machine_tags,
    )

    print("machine add result", create_result)

    return create_result.code


def _machine_remove(cluster: models.Cluster, machine_name: str) -> int:
    """
    Remove machine from cluster.
    """
    list_result = services.machines.list(cluster=cluster)

    if machine_name:
        # get specific machine
        machines_map = list_result.objects_map
        machine = machines_map.get(machine_name)
    else:
        # get any machine
        machine = list_result.objects_list[0]

    if not machine:
        return -1

    services.hetzner.servers.delete(id=machine.id)

    return 0
