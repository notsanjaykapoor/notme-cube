import dataclasses
import os
import time

import hcloud
import hcloud.images
import hcloud.locations
import hcloud.server_types
import hcloud.ssh_keys

import models
import services.hetzner.servers


@dataclasses.dataclass
class Struct:
    code: int
    machine: models.Machine
    seconds: int
    server: dict
    errors: list[str]


def create(cluster: models.Cluster, name: str, ssh_key: str, tags: dict) -> Struct:
    """
    create hetzner cluster server
    """
    struct = Struct(
        code=0,
        machine=None,
        seconds=0,
        server={},
        errors=[],
    )

    t1 = time.time()

    try:
        client = hcloud.Client(token=os.environ.get("VPS_HETZNER_TOKEN"))

        response = client.servers.create(
            automount=False,
            image=hcloud.images.Image(name=cluster.server_image),
            labels=tags,
            location=hcloud.locations.Location(name=cluster.server_location),
            name=name,
            server_type=hcloud.server_types.ServerType(name=cluster.server_type),
            ssh_keys=[hcloud.ssh_keys.SSHKey(name=ssh_key)],
            start_after_create=True,
        )

        response.action.wait_until_finished()

        struct.server = response.server
        struct.machine = services.hetzner.servers.machine_from_server(server=struct.server)
    except Exception as e:
        struct.code = 500
        struct.errors.append(e.message)

    struct.seconds = round(time.time() - t1, 2)

    return struct
