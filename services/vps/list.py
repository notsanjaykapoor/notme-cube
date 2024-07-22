import dataclasses
import os
import subprocess
import time

import hcloud

import models

@dataclasses.dataclass
class Struct:
    code: int
    map: dict[str, models.Machine]
    objects: list[models.Machine]
    seconds: int
    errors: list[str]


def list(cloud: str, query: str) -> Struct:
    if cloud not in [models.machine.CLOUD_GCP, models.machine.CLOUD_HETZNER]:
        raise ValueError(f"cloud {cloud} invalid")

    if cloud == models.machine.CLOUD_GCP:
        result = _list_gcp(query=query)
    elif cloud == models.machine.CLOUD_HETZNER:
        result = _list_hetzner(query=query)

    return result


def _list_gcp(query: str) -> Struct:
    struct = Struct(
        code=0,
        map={},
        objects=[],
        seconds=0,
        errors=[],
    )

    t1 = time.time()

    cmd = "gcloud compute instances list"
    response = subprocess.run(cmd, shell=True, capture_output=True)
    struct.code = response.returncode
    struct.seconds = round(time.time() - t1, 2)

    if struct.code != 0:
        struct.errors.append(response.stderr.decode("utf-8"))
        return struct

    field_map = {}

    lines = response.stdout.decode("utf-8").split("\n")
    for line_i, line in enumerate(lines):
        tokens = line.strip().split()
        
        if not tokens:
            continue

        if line_i == 0:
            # header
            # name, zone, machine_type, preemptible, internal_ip, external_ip, status
            for token_i, token in enumerate(tokens):
                field_map[token_i] = token.lower()
        else:
            # body
            if len(tokens) < len(field_map):
                # fill in blank 'preemptible' field
                tokens = tokens[0:3] + [""] + tokens[3:7]

            machine = models.Machine(
                cloud=models.machine.CLOUD_GCP,
                id="",
                ip="",
                name="",
                state="",
                user=os.environ.get("VPS_GCP_USER"),
            )

            for token_i, token in enumerate(tokens):
                field = field_map.get(token_i)

                if field == "external_ip":
                    machine.ip = token
                elif field == "name":
                    machine.id = token
                    machine.name = token
                elif field == "status":
                    machine.state = token.lower()

            if not query or query in machine.name:
                struct.map[machine.name] = machine
                struct.objects.append(machine)

    struct.objects = sorted(struct.objects, key=lambda o: o.name)

    return struct         


def _list_hetzner(query: str) -> Struct:
    struct = Struct(
        code=0,
        map={},
        objects=[],
        seconds=0,
        errors=[],
    )

    t1 = time.time()

    client = hcloud.Client(token=os.environ.get("VPS_HETZNER_TOKEN"))
    servers = client.servers.get_all()

    struct.seconds = round(time.time() - t1, 2)

    for server in servers:
        machine = models.Machine(
            cloud=models.machine.CLOUD_HETZNER,
            id=server.id,
            ip=server.public_net.ipv4.ip,
            name=server.name,
            state=server.status,
            user=os.environ.get("VPS_HETZNER_USER"),
        )

        if not query or query in machine.name:
            struct.map[machine.name] = machine
            struct.objects.append(machine)

    return struct
