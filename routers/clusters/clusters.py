import time

import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.clusters
import services.hetzner.servers
import services.hetzner.ssh_keys
import services.users
import services.vps

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

@app.get("/clusters/{cluster_id}/add")
def cluster_add(
    request: fastapi.Request,
    cluster_id: int,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    Add a cluster machine.
    """
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    logger.info(f"{context.rid_get()} cluster {cluster_id} add")

    try:
        cluster = services.clusters.get_by_id(db_session=db_session, id=cluster_id)

        list_result = services.vps.list(cloud=cluster.cloud, query=f"cluster:{cluster.name}")
        machines_list = list_result.objects

        # generate new machine name
        machine_names = [machine.name for machine in machines_list]
        machine_name = services.clusters.machine_name_generate(cluster=cluster, names=machine_names)

        # get primary ssh key
        ssh_keys_struct = services.hetzner.ssh_keys.list()
        ssh_key_name = ssh_keys_struct.objects[0].name

        # generate machine tag
        machine_tags = {
            "cluster": cluster.name,
        }

        cluster.size_ask += 1
        db_session.add(cluster)
        db_session.commit()

        # add machine to cluster
        services.hetzner.servers.create(cluster=cluster, name=machine_name, ssh_key=ssh_key_name, tags=machine_tags)
        # time.sleep(10)

        cluster.size_has += 1
        db_session.add(cluster)
        db_session.commit()

        logger.info(f"{context.rid_get()} cluster {cluster_id} add ok - machine '{machine_name}'")
    except Exception as e:
        logger.error(f"{context.rid_get()} cluster {cluster_id} add exception '{e}'")

    return fastapi.responses.RedirectResponse(f"/clusters/{cluster.id}/machines")


@app.get("/clusters/{cluster_id}/machines")
def cluster_show(
    request: fastapi.Request,
    cluster_id: int | str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    List all cluster machines.

    This method shares the machines 'list' method.
    """
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    logger.info(f"{context.rid_get()} cluster {cluster_id}")

    machines_list = []
    query = ""
    query_code = 0
    query_result = ""
    query_seconds = 0

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        cluster = services.clusters.get_by_id_or_name(db_session=db_session, id=cluster_id)
        list_result = services.vps.list(cloud=cluster.cloud, query=f"cluster:{cluster.name}")
        machines_list = list_result.objects
        query_seconds += list_result.seconds
    except Exception as e:
        query_code = 500
        logger.error(f"{context.rid_get()} clusters show exception '{e}'")

    if "HX-Request" in request.headers:
        template = "machines/list_table.html"
    else:
        template = "machines/list.html"

    logger.info(f"{context.rid_get()} cluster {cluster_id} ok")

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Cluster Machines",
                "cluster": cluster,
                "machines_list": machines_list,
                "prompt_text": "",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} clusters show render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response


@app.get("/clusters/{cluster_id}/sync")
def cluster_sync(
    request: fastapi.Request,
    cluster_id: int,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    logger.info(f"{context.rid_get()} cluster {cluster_id} sync")

    sync_struct = services.clusters.sync(db_session=db_session, cluster_id=cluster_id)

    logger.info(f"{context.rid_get()} cluster {cluster_id} sync ok - changes {sync_struct.changes}")

    return fastapi.responses.RedirectResponse("/clusters")


@app.get("/clusters")
def clusters_list(
    request: fastapi.Request,
    query: str = "",
    offset: int=0,
    limit: int=50,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    List all clusters
    """
    logger.info(f"{context.rid_get()} clusters list query '{query}'")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    clusters_list = []
    query_seconds = 0

    try:
        clusters_result = services.clusters.list(db_session=db_session, query=query, offset=offset, limit=limit)
        clusters_list = clusters_result.objects
        query_code = 0
        query_result = f"query '{query}' returned {len(clusters_list)} results in {query_seconds}s"
    except Exception as e:
        query_code = 500
        logger.error(f"{context.rid_get()} clusters list exception '{e}'")

    if "HX-Request" in request.headers:
        template = "clusters/list_table.html"
    else:
        template = "clusters/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Clusters",
                "clusters_list": clusters_list,
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} clusters list render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response
