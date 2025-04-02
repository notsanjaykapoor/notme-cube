import datetime

import sqlmodel

import context
import log
import models
import services.clusters
import services.cube.deploys
import services.cube.pods
import services.cube.projects


def deploy(db_session: sqlmodel.Session, deploy: models.CubeDeploy) -> int:
    """
    Deploy a project and all of its pods to a cluster.
    """
    logger = log.init("app")

    cluster = services.clusters.get_by_id(db_session=db_session, id=deploy.cluster_id)
    project = services.cube.projects.get_by_name(name=deploy.project_name)

    code = 0

    if not cluster:        
        logger.error(f"{context.rid_get()} deploy {deploy.id} invalid cluster {deploy.cluster_id}")
        code = 422

    if not project:
        logger.error(f"{context.rid_get()} deploy {deploy.id} invalid project '{deploy.project.name}'")
        code = 422


    if code != 0:
        deploy.state = models.cube_deploy.STATE_ERROR
        db_session.add(deploy)
        db_session.commit()
        return code

    deploy.state = models.cube_deploy.STATE_DEPLOYING
    db_session.add(deploy)
    db_session.commit()

    logger.info(f"{context.rid_get()} deploy {deploy.id} project '{project.name}' cluster '{cluster.name}' try")

    list_result = services.cube.pods.list(projects=[project])

    try:
        for pod in list_result.pods:
            deploy_struct = services.cube.deploys.deploy_pod(
                project=project,
                pod=pod,
                cluster=cluster,
            )

            if deploy_struct.code != 0:
                raise Exception(f"deploy pod exception {deploy_struct.code}")

        deploy.deploy_at = datetime.datetime.now(datetime.timezone.utc)
        deploy.state = models.cube_deploy.STATE_DEPLOYED
    except Exception as e:
        deploy.data = {
            "error": str(e),
        }
        deploy.state = models.cube_deploy.STATE_ERROR

    db_session.add(deploy)
    db_session.commit()

    logger.info(f"{context.rid_get()} deploy {deploy.id} project '{project.name}' cluster '{cluster.name}' ok")

    return 0
