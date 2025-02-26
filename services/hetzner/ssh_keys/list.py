import dataclasses
import os
import time

import hcloud


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[dict]
    seconds: int
    errors: list[str]


def list() -> Struct:
    """
    list hetzner ssh keys
    """
    struct = Struct(
        code=0,
        objects=[],
        seconds=0,
        errors=[],
    )

    t1 = time.time()

    client = hcloud.Client(token=os.environ.get("VPS_HETZNER_TOKEN"))
    struct.objects = client.ssh_keys.get_all()

    struct.seconds = round(time.time() - t1, 2)

    return struct

