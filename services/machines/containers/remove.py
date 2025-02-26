import dataclasses

import models
import services.ssh

@dataclasses.dataclass
class Struct:
    code: int
    seconds: int
    errors: list[str]


def remove(machine: models.Machine, service: str) -> Struct:
    """
    Remove container 'service' on the specified machine.
    """
    struct = Struct(
        code=0,
        seconds=0,
        errors=[],
    )

    struct.code, result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=f"docker rm {service}")

    if struct.code != 0:
        struct.errors.append(result)
        return struct

    return struct
