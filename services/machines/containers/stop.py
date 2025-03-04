import dataclasses

import models
import services.machines.containers
import services.ssh

@dataclasses.dataclass
class Struct:
    code: int
    containers: list[models.Container]
    errors: list[str]


def stop(machine: models.Machine) -> Struct:
    """
    Stop all container on the specified machine. 
    """
    struct = Struct(
        code=0,
        containers=[],
        errors=[],
    )

    list_result = services.machines.containers.list(machine=machine, query="")

    for container in list_result.objects_list:
        if container.name == models.service.SERVICE_DOCKER:
            continue

        docker_stop_cmd = f"docker stop {container.name}"

        struct.code, result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=docker_stop_cmd)

        if struct.code != 0:
            struct.errors.append(result)
            return struct

        struct.containers.append(container)

    return struct
