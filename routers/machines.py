import os

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
import main_shared
import services.ssh
import services.vps
import services.vps.containers
import services.vps.nats

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]


@app.get("/machines/{machine_name}/containers")
def machine_containers_list(
    request: fastapi.Request,
    machine_name: str,
    cloud: str,
    query: str="",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} machine '{machine_name}' containers")

    try:
        list_result = services.vps.list(cloud=cloud, query=machine_name)
        machines_map = list_result.map
        machine = machines_map.get(machine_name)

        if not machine:
            return fastapi.responses.RedirectResponse("/machines")

        list_result = services.vps.containers.list(ip=machine.ip, user=services.ssh.user(), query=query)
        containers_list = list_result.objects

        query_code = list_result.code
        query_result = f"query '{query}' returned {len(containers_list)} results in {list_result.seconds}s"
    except Exception as e:
        logger.error(f"{context.rid_get()} machines containers exception '{e}'")

    if "HX-Request" in request.headers:
        template = "machines/containers/list_table.html"
    else:
        template = "machines/containers/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": f"Containers : {machine.name}",
                "app_version": app_version,
                "containers_list": containers_list,
                "machine": machine,
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} machines containers render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response


@app.get("/machines/{machine_name}/nats")
def machine_nats_list(
    request: fastapi.Request,
    machine_name: str,
    cloud: str,
    query: str="",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} machine '{machine_name}' nats")

    try:
        list_result = services.vps.list(cloud=cloud, query=machine_name)
        machines_map = list_result.map
        machine = machines_map.get(machine_name)

        if not machine:
            return fastapi.responses.RedirectResponse("/machines")
    except Exception as e:
        logger.error(f"{context.rid_get()} machines containers exception '{e}'")

    if "HX-Request" in request.headers:
        template = "machines/nats/list_table.html"
    else:
        template = "machines/nats/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": f"Nats : {machine.name}",
                "app_version": app_version,
                "machine": machine,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} machines nats render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response


@app.get("/machines")
def machines_list(
    request: fastapi.Request,
    cloud: str="",
    query: str = "",
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    clouds_list = services.vps.clouds()

    logger.info(f"{context.rid_get()} machines list clouds {clouds_list} query '{query}'")

    machines_list = []
    query_seconds = 0

    for cloud in clouds_list:
        list_result = services.vps.list(cloud=cloud, query=query)
        machines_list.extend(list_result.objects)
        query_seconds += list_result.seconds
        query_code = list_result.code

    for machine in machines_list:
        # check nat
        if services.vps.nats.check(ip=machine.ip) == 0:
            # nat server exists
            machine.nats = 1

    query_result = f"query '{query}' returned {len(machines_list)} results in {query_seconds}s"

    if "HX-Request" in request.headers:
        template = "machines/list_table.html"
    else:
        template = "machines/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Machines",
                "app_version": app_version,
                "machines_list": machines_list,
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} machines list render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response
