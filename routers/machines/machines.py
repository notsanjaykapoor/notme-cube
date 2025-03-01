import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.clouds
import services.clusters
import services.hetzner.servers
import services.users
import services.machines
import services.machines.containers

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


# deprecated
@app.get("/clusters/{cluster_id}/machines/{machine_name}/delete")
def machines_delete(
    request: fastapi.Request,
    cluster_id: int | str,
    machine_name: str,
    cloud: str=services.clouds.default(),
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} cluster '{cluster_id}' machine '{machine_name}' delete")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    http_referer = request.headers.get("referer")

    try:
        cluster = services.clusters.get_by_id_or_name(db_session=db_session, id=cluster_id)

        list_result = services.machines.list(cluster=cluster)
        machines_map = list_result.objects_map
        machine = machines_map.get(machine_name)

        if not machine:
            return fastapi.responses.RedirectResponse(http_referer)
        
        cluster.size_ask -= 1
        db_session.add(cluster)
        db_session.commit()

        services.hetzner.servers.delete(id=machine.id)

        cluster.size_has -= 1
        db_session.add(cluster)
        db_session.commit()

        logger.info(f"{context.rid_get()} cluster '{cluster}' machine '{machine_name}' delete ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} cluster '{cluster}' machine '{machine_name}' delete exception '{e}'")

    return fastapi.responses.RedirectResponse(http_referer)
