import dataclasses
import os
import time

import hcloud
import hcloud.servers


@dataclasses.dataclass
class Struct:
    code: int
    seconds: int
    status: str
    errors: list[str]


def delete(id: int) -> Struct:
    """
    delete hetzner server
    """
    struct = Struct(
        code=0,
        seconds=0,
        status="",
        errors=[],
    )

    t1 = time.time()

    try:
        client = hcloud.Client(token=os.environ.get("VPS_HETZNER_TOKEN"))

        response = client.servers.delete(
            server=hcloud.servers.Server(id=id),
        )

        response.wait_until_finished()

        struct.status = response.status
    except Exception as e:
        struct.code = 500
        struct.errors.append(e.message)

    struct.seconds = round(time.time() - t1, 2)

    return struct
