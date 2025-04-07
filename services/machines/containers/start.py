import dataclasses

import models
import services.machines.containers

@dataclasses.dataclass
class Struct:
    code: int
    container: models.Container
    seconds: int
    errors: list[str]


def start(machine: models.Machine, service: str) -> Struct:
    """
    Start container 'service' on the specified machine.
    """
    struct = Struct(
        code=0,
        container=None,
        seconds=0,
        errors=[],
    )

    list_result = services.machines.containers.list(machine=machine, query="")

    if service in list_result.objects_map.keys():
        struct.code = 409
        struct.container = list_result.objects_map.get(service)
        struct.errors.append(f"container '{service}' already running")
        return struct

    return services.machines.containers.start_service(machine=machine, service=service)
