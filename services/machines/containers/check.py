import dataclasses

import models
import services.machines.containers

@dataclasses.dataclass
class Struct:
    code: int
    containers_missing: list[models.Container]
    containers_running: list[models.Container]
    containers_status: int
    docker_status: int
    errors: list[str]


def check(machine: models.Machine) -> Struct:
    """
    Check docker and containers on machine.

    Returns status of containers configured vs what is actually running.
    """
    struct = Struct(
        code=0,
        containers_missing=[],
        containers_running=[],
        containers_status=0,
        docker_status=0,
        errors=[],
    )

    list_result = services.machines.containers.list(machine=machine, query="")

    print("containers list ", list_result) # xxx

    if list_result.code == 127:
        # docker not running
        struct.docker_status = list_result.code

    services_list = [s for s in machine.services.split(",") if s]

    struct.containers_running = list_result.objects_list
    struct.containers_missing.extend(
        _containers_build(services=set(services_list) - set(list_result.objects_map.keys()))
    )

    if not services:
        return struct

    for container in struct.containers_missing:
        struct.errors.append(f"container '{container.name}' down")
        struct.containers_status = 404

    return struct


def _containers_build(services: list[str]) -> list[models.Container]:
    """
    build container objects from services list
    """
    containers = []

    for service in services:
        container = models.Container(
            id="",
            image="",
            name=service,
            state=models.container.STATE_DOWN,
        )
        containers.append(container)

    return containers


