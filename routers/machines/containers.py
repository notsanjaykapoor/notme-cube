import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.clouds
import services.clusters
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


@app.get("/clusters/{cluster_id}/machines/{machine_name}/containers")
def machines_containers_list(
    request: fastapi.Request,
    cluster_id: str,
    machine_name: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} cluster '{cluster_id}' machine '{machine_name}' containers list try")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        cluster = services.clusters.get_by_id_or_name(db_session=db_session, id=cluster_id)

        list_result = services.machines.list(cluster=cluster)
        machines_map = list_result.objects_map
        machine = machines_map.get(machine_name)

        if not machine:
            return fastapi.responses.RedirectResponse("/machines")

        check_result = services.machines.containers.check(machine=machine)
        containers_list = check_result.containers_running + check_result.containers_missing

        if check_result.code == 0:
            logger.info(f"{context.rid_get()} cluster '{cluster_id}' machine '{machine_name}' containers list ok")
        else:
            logger.error(f"{context.rid_get()} cluster '{cluster_id}' machine '{machine_name}' containers list error - {check_result.errors}")
    except Exception as e:
        logger.error(f"{context.rid_get()} cluster '{cluster_id}' machines containers list exception '{e}'")

    if "HX-Request" in request.headers:
        template = "machines/containers/list_table.html"
    else:
        template = "machines/containers/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Machine Containers",
                "cluster": cluster,
                "containers_list": containers_list,
                "machine": machine,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} machines containers render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response


@app.get("/machines/{machine_name}/containers/remove")
def machines_containers_remove(
    request: fastapi.Request,
    machine_name: str,
    service: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    cluster_id = machine_name.split("-")[0]

    logger.info(f"{context.rid_get()} cluster '{cluster_id}' machine '{machine_name}' container '{service}' remove")

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

        start_result = services.machines.containers.remove(machine=machine, service=service)

        if start_result.code == 0:
            logger.info(f"{context.rid_get()} machine '{machine_name}' container '{service}' remove ok")
        else:
            logger.error(f"{context.rid_get()} machine '{machine_name}' container '{service}' remove error {start_result.code}")
    except Exception as e:
        logger.error(f"{context.rid_get()} machines '{machine_name}' container '{service}' remove exception '{e}'")

    return fastapi.responses.RedirectResponse(http_referer)


@app.get("/machines/{machine_name}/containers/start")
def machines_containers_start(
    request: fastapi.Request,
    machine_name: str,
    service: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    cluster_id = machine_name.split("-")[0]

    logger.info(f"{context.rid_get()} cluster '{cluster_id}' machine '{machine_name}' container '{service}' start")

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

        start_result = services.machines.containers.start(machine=machine, service=service)

        if start_result.code == 0:
            logger.info(f"{context.rid_get()} cluster '{cluster_id}' machine '{machine_name}' container '{service}' start ok")
        else:
            logger.error(f"{context.rid_get()} cluster '{cluster_id}' machine '{machine_name}' container '{service}' start error {start_result.code}")
    except Exception as e:
        logger.error(f"{context.rid_get()} cluster '{cluster_id}' machines '{machine_name}' container '{service}' start exception '{e}'")

    return fastapi.responses.RedirectResponse(http_referer)