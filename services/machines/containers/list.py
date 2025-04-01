import dataclasses
import json
import time
import typing

import models
import services.ssh


@dataclasses.dataclass
class Struct:
    code: int
    objects_map: dict[str, models.Container]
    objects_list: list[models.Container]
    seconds: int
    errors: list[str]


def list(machine: models.Machine, query: str) -> Struct:
    """
    Get list of containers on specified machine.
    """
    struct = Struct(
        code=0,
        objects_map={},
        objects_list=[],
        seconds=0,
        errors=[],
    )

    t1 = time.time()

    cmd_running = "docker ps -a --format '{{json .}}'"
    struct.code, result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=cmd_running)

    if struct.code == 255:
        # clear hosts file first, then run command again
        services.ssh.ssh_hosts_remove(host=machine.ip)
        struct.code, result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=cmd_running)

    struct.seconds = round(time.time() - t1, 2)

    if struct.code != 0:
        # docker error
        struct.errors.append(result)
        return struct

    # add docker container to list

    container = models.Container(
        id="",
        image="",
        name="docker",
        state=models.container.STATE_RUNNING,
    )
    struct.objects_list.append(container)

    # add running containers to list

    struct.objects_list.extend(
        _docker_json_parse(docker_ps=result, query=query)
    )

    # update objects map

    for container in struct.objects_list:
        struct.objects_map[container.name] = container

    return struct         


def _docker_json_parse(docker_ps: str, query: str) -> typing.List[models.Container]:
    """
    Parse docker ps json result into a list of containers.
    """
    containers = []

    json_lines = [json.loads(line) for line in docker_ps.split("\r\n") if line]

    for json_object in json_lines:
        container = models.Container(
            id=json_object.get("ID"),
            image=json_object.get("Image"),
            name=json_object.get("Names"),
            networks=json_object.get("Networks"),
            ports=json_object.get("Ports", ""),
            state=json_object.get("State").lower(),
            uptime=json_object.get("Status", "").lower(),
        )

        containers.append(container)

    return containers


def _docker_ps_parse(docker_ps: str, query: str, state: str) -> typing.List[models.Container]:
    """
    Parse docker ps result into a list of containers.
    """
    containers = []

    field_map = {}

    docker_ps_lines = docker_ps.split("\r\n")

    for line_i, line in enumerate(docker_ps_lines):
        tokens = line.strip().split()
        
        if not tokens:
            continue

        if line_i == 0:
            # header fields - ['container id', 'image', 'command', 'created', 'status', 'ports', 'names']
            # header, filter tokens and keep: 'container id', 'image', 'names'
            field_map[0] = "id"
            field_map[1] = "image"
            field_map[2] = "name"
        else:
            # body, filter tokens and keep: 'id', 'image', 'status' 'names'
            tokens = tokens[0:2] + [tokens[-1]]

            container = models.Container(
                id="",
                image="",
                name="",
                state=state,
            )

            for token_i, token in enumerate(tokens):
                field = field_map.get(token_i)

                if field == "id":
                    container.id = token
                elif field == "image":
                    container.image = token
                elif field == "name":
                    container.name = token

            if not query or query in container.name:
                containers.append(container)

    return containers
