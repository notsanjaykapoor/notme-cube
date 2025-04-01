import dataclasses

import sqlmodel

import models


@dataclasses.dataclass
class Struct:
    code: int
    deploy: models.CubeDeploy
    errors: list[str]


def create(
    db_session: sqlmodel.Session,
    cluster: models.Cluster,
    project: models.CubeProject,
) -> Struct:
    """
    """
    struct = Struct(
        code = 0,
        deploy=None,
        errors=[],
    )

    struct.deploy = models.CubeDeploy(
        cluster_id=cluster.id,
        project_name=project.name,
        state=models.cube_deploy.STATE_QUEUED,
    )
    try:
        db_session.add(struct.deploy)
        db_session.commit()
    except Exception:
        db_session.rollback()
        struct.code = 500


    return struct