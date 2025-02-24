import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.clusters
import services.hetzner.servers
import services.users
import services.vps
import services.vps.containers
import services.vps.nats

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/machines/{machine_name}/delete")
def machine_delete(
    request: fastapi.Request,
    machine_name: str,
    cloud: str,
    cluster: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} cluster '{cluster}' machine '{machine_name}' delete")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    http_referer = request.headers.get("referer")

    try:
        list_result = services.vps.list(cloud=cloud, query=machine_name)
        machines_map = list_result.map
        machine = machines_map.get(machine_name)

        if not machine:
            return fastapi.responses.RedirectResponse(http_referer)
        
        cluster = services.clusters.get_by_id_or_name(db_session=db_session, id=cluster)

        cluster.size_ask -= 1
        db_session.add(cluster)
        db_session.commit()

        services.hetzner.servers.delete(id=machine.id)

        cluster.size_has -= 1
        db_session.add(cluster)
        db_session.commit()
    except Exception as e:
        logger.error(f"{context.rid_get()} machine delete exception '{e}'")

    logger.info(f"{context.rid_get()} cluster '{cluster}' machine '{machine_name}' delete ok")

    return fastapi.responses.RedirectResponse(http_referer)



@app.get("/machines")
def machines_list(
    request: fastapi.Request,
    cloud: str="",
    query: str = "",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    List all machines.

    This method shares a view with the cluster 'show' method.
    """
    clouds_list = services.vps.clouds()

    logger.info(f"{context.rid_get()} machines list clouds {clouds_list} query '{query}'")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    machines_list = []
    query_seconds = 0

    try:
        for cloud in clouds_list:
            list_result = services.vps.list(cloud=cloud, query=query)
            machines_list.extend(
                sorted(list_result.objects, key=lambda m: m.name)
            )
            query_seconds += list_result.seconds
            query_code = list_result.code

        query_seconds = round(query_seconds, 2)

        for machine in machines_list:
            # check nat
            if services.vps.nats.check(ip=machine.ip) == 0:
                # nat server exists
                machine.nats = 1

        query_result = f"query '{query}' returned {len(machines_list)} results in {query_seconds}s"
    except Exception as e:
        logger.error(f"{context.rid_get()} machines list exception '{e}'")

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
                "machines_list": machines_list,
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} machines list render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response


@app.get("/machines/{machine_name}/containers")
def machines_list_containers(
    request: fastapi.Request,
    machine_name: str,
    cloud: str,
    cluster: str,
    query: str="",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} cluster '{cluster}' machine '{machine_name}' containers")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        list_result = services.vps.list(cloud=cloud, query=machine_name)
        machines_map = list_result.map
        machine = machines_map.get(machine_name)

        if not machine:
            return fastapi.responses.RedirectResponse("/machines")

        list_result = services.vps.containers.list(ip=machine.ip, user=machine.user, query=query)
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
                "cluster": cluster,
                "containers_list": containers_list,
                "machine": machine,
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} machines containers render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response


@app.get("/machines/{machine_name}/nats")
def machines_list_nats(
    request: fastapi.Request,
    machine_name: str,
    cloud: str,
    cluster: str,    
    query: str="",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} cluster '{cluster}' machine '{machine_name}' nats")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

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
                "machine": machine,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} machines nats render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response


