import os

import models


def machine_from_server(server) -> models.Machine:
    """
    Create machine object from hetzner server object
    """
    machine = models.Machine(
        cloud=models.machine.CLOUD_HETZNER,
        id=server.id,
        image=server.image.name,
        ip=server.public_net.ipv4.ip,
        location=server.datacenter.location.name,
        name=server.name,
        state=server.status,
        tags=server.labels,
        type=server.server_type.name,
        user=os.environ.get("VPS_HETZNER_USER"),
    )

    return machine
