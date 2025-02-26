import dataclasses
import re

import sqlalchemy
import sqlmodel

import models
import services.clusters
import services.hetzner.servers
import services.mql

@dataclasses.dataclass
class Struct:
    code: int
    changes: int
    errors: list[str]


def sync(db_session: sqlmodel.Session, cluster_id: int | str) -> Struct:
    """
    Sync cluster state

    The sync process checks the number of physical machines in the cluster vs the count in the cluster database object and
    resolves any discrepancies.
    """
    struct = Struct(
        code=0,
        changes=0,
        errors=[],
    )

    cluster = services.clusters.get_by_id_or_name(
        db_session=db_session,
        id=cluster_id,
    )

    servers_struct = services.hetzner.servers.list(query=f"cluster:{cluster.name}")

    server_machines = servers_struct.objects_list
    server_count = len(server_machines)

    if server_count != cluster.size_ask:
        cluster.size_ask = server_count
        struct.changes += 1

    if server_count != cluster.size_has:
        cluster.size_has = server_count
        struct.changes += 1

    if struct.changes > 0:
        db_session.add(cluster)
        db_session.commit()

    return struct
