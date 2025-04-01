import multiprocessing
import time

import context
import log
import services.cube.deploys
import services.database.session


def deploy_task():
    """
    Check for queued deploys and deploy them sequentially.

    This can be run as a background task/process on app startup.
    """
    logger = log.init("app")

    logger.info(f"{context.rid_get()} deploy task starting")

    task_rid = context.rid_get()

    while True:
        with services.database.session.get() as db_session:
            list_result = services.cube.deploys.list(
                db_session=db_session,
                query="state:queued",
                offset=0,
                limit=1,
                sort="id+"
            )

            if list_result.count == 1:
                cube_deploy = list_result.objects[0]

                # set task request id
                context.rid_set(id=f"{task_rid}-{cube_deploy.id}")

                services.cube.deploys.deploy(
                    db_session=db_session,
                    deploy=cube_deploy,
                )

            time.sleep(5)


