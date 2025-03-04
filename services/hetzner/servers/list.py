import dataclasses
import os
import time

import hcloud

import models
import services.hetzner.servers

@dataclasses.dataclass
class Struct:
    code: int
    objects_list: list[models.Machine]
    objects_map: dict[str, models.Machine]
    seconds: int
    errors: list[str]


def list(query: str=""):
    """
    list hetzner servers
    """
    struct = Struct(
        code=0,
        objects_list=[],
        objects_map={},
        seconds=0,
        errors=[],
    )

    t1 = time.time()

    client = hcloud.Client(token=os.environ.get("VPS_HETZNER_TOKEN"))
    servers = client.servers.get_all()

    query_norm = _query_normalize(query=query)

    struct.seconds = round(time.time() - t1, 2)

    for server in servers:
        machine = services.hetzner.servers.machine_from_server(server=server)

        if not query_norm:
            struct.objects_map[machine.name] = machine
            struct.objects_list.append(machine)
        else:
            key, value = query_norm.split(":")

            if key == "name" and value in machine.name:
                # machine name match
                struct.objects_map[machine.name] = machine
                struct.objects_list.append(machine)
            elif value == machine.tags.get(key):
                # machine label value match
                struct.objects_map[machine.name] = machine
                struct.objects_list.append(machine)

    return struct


def _query_normalize(query: str) -> str:
    if not query:
        return query
    
    if ":" not in query:
        return f"name:{query}" # default query field
    
    return query