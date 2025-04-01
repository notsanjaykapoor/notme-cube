import dataclasses
import glob

import yaml

import models

@dataclasses.dataclass
class Struct:
    code: int
    pods: list[models.CubePod]
    errors: list[str]


def list(projects: list[models.CubeProject]) -> Struct:
    """
    List all pods from the specified list of projects.
    """
    struct = Struct(
        code=0,
        pods=[],
        errors=[],
    )

    for project in projects:
        # parse all project yml files
        pattern = f"{project.dir}/*.yml"
        files = glob.glob(pattern)

        for file in files:
            with open(file, "r") as f:
                data = yaml.safe_load(f)

                containers = data.get("spec", {}).get("containers", [])
                container = containers[0]

                pod = models.CubePod(
                    c_command=container.get("command"),
                    c_env=container.get("env"),
                    c_image=container.get("image"),
                    c_name=container.get("name"),
                    c_network=container.get("network", ""),  
                    c_ports=container.get("ports"),
                    project_name=project.name,
                )

                struct.pods.append(pod)

    return struct