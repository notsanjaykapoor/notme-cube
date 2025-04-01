import dataclasses
import os
import re

import yaml

import models
import services.files

@dataclasses.dataclass
class Struct:
    code: int
    count: int
    projects: list[models.CubeProject]
    errors: list[str]


def list(path: str, query: str="") -> Struct:
    """
    List all projects matching optional query param.
    """
    struct = Struct(
        code=0,
        count=0,
        projects=[],
        errors=[],
    )

    if not os.path.exists(path):
        struct.code = 404
        return struct

    with open(path, "r") as file:
        data = yaml.safe_load(file)

    for object in data.get("projects"):
        name = object.get("name")

        if query and not re.search(rf"{query}", name):
            continue

        location = object.get("location")
        _, source_dir, _ = services.files.file_uri_parse(source_uri=location)

        project = models.CubeProject(
            name=name,
            dir=source_dir,
        )

        struct.projects.append(project)

    struct.count = len(struct.projects)

    return struct