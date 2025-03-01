import dataclasses
import os
import subprocess
import time

import sqlmodel

import models
import services.clusters
import services.hetzner.servers


@dataclasses.dataclass
class Struct:
    code: int
    objects_map: dict[str, models.Machine]
    objects_list: list[models.Machine]
    seconds: int
    errors: list[str]


def list(cluster: models.Cluster) -> Struct:
    if not cluster:
        raise ValueError(f"cluster invalid")

    if cluster.cloud == models.machine.CLOUD_GCP:
        result = _list_gcp(query="")
    elif cluster.cloud == models.machine.CLOUD_HETZNER:
        result = services.hetzner.servers.list(query=f"cluster:{cluster.name}")
    else:
        raise ValueError(f"cloud {cluster.cloud} invalid")

    return result


def _list_gcp(query: str) -> Struct:
    struct = Struct(
        code=0,
        objects_map={},
        objects_list=[],
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
                struct.objects_map[machine.name] = machine
                struct.objects_list.append(machine)

    struct.objects_list = sorted(struct.objects_list, key=lambda o: o.name)

    return struct         
