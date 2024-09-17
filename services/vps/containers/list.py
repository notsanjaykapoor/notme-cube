import dataclasses
import time

import models
import services.ssh


@dataclasses.dataclass
class Struct:
    code: int
    map: dict[str, models.Machine]
    objects: list[models.Machine]
    seconds: int
    errors: list[str]


def list(ip: str, user: str, query: str) -> Struct:
    struct = Struct(
        code=0,
        map={},
        objects=[],
        seconds=0,
        errors=[],
    )

    t1 = time.time()

    cmd = "docker ps"
    struct.code, result = services.ssh.exec(host=ip, user=user, cmd=cmd)
    struct.seconds = round(time.time() - t1, 2)

    if struct.code != 0:
        struct.errors.append(result)
        return struct

    field_map = {}

    lines = result.split("\r\n")

    for line_i, line in enumerate(lines):
        tokens = line.strip().split()
        
        if not tokens:
            continue

        if line_i == 0:
            # header, filter tokens and keep: 'container', 'image', 'names'
            field_map[0] = "id"
            field_map[1] = "image"
            field_map[2] = "name"
        else:
            # body, filter tokens and keep: 'id', 'image', 'names'
            tokens = tokens[0:2] + [tokens[-1]]

            container = models.Container(
                id="",
                image="",
                name="",
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
                struct.map[container.name] = container
                struct.objects.append(container)

    struct.objects = sorted(struct.objects, key=lambda o: o.name)

    return struct         

