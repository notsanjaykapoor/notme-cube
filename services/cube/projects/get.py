import models
import services.cube
import services.cube.projects


def get_by_name(name: str) -> models.CubeProject | None:
    list_result = services.cube.projects.list(
        path=services.cube.config_path(),
        query=name,
    )

    if list_result.count == 0:
        return None

    return list_result.projects[0]