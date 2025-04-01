import sqlmodel

import models
import services.cube.deploys


def test_deploys_list(
    db_session: sqlmodel.Session,
    cluster_1: models.Cluster,
    project_1: models.CubeProject,
):
    # create 2 deploy objects

    deploy_struct = services.cube.deploys.create(
        db_session=db_session,
        cluster=cluster_1,
        project=project_1,
    )

    assert deploy_struct.code == 0
    assert deploy_struct.deploy.id

    deploy_1 = deploy_struct.deploy

    deploy_struct = services.cube.deploys.create(
        db_session=db_session,
        cluster=cluster_1,
        project=project_1,
    )

    assert deploy_struct.code == 0
    assert deploy_struct.deploy.id

    deploy_2 = deploy_struct.deploy

    # list all

    list_result = services.cube.deploys.list(
        db_session=db_session,
        query="",
        offset=0,
        limit=20,
        sort="id-"
    )

    assert list_result.code == 0
    assert list_result.count == 2
    assert list_result.total == 2

    deploy = list_result.objects[0]

    assert deploy.cluster_id == cluster_1.id
    assert deploy.id == deploy_2.id
    assert deploy.project_name == project_1.name
    assert deploy.state == "queued"

    # list oldest queued deploy

    list_result = services.cube.deploys.list(
        db_session=db_session,
        query="state:queued",
        offset=0,
        limit=1,
        sort="id+"
    )

    assert list_result.code == 0
    assert list_result.count == 1
    assert list_result.total == 2

    deploy = list_result.objects[0]

    assert deploy.cluster_id == cluster_1.id
    assert deploy.id == deploy_1.id
    assert deploy.project_name == project_1.name
    assert deploy.state == "queued"

    db_session.delete(deploy_1)
    db_session.delete(deploy_2)
    db_session.commit()
