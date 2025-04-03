import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import models
import services.clusters
import services.machines
import services.users

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

@app.get("/clusters/{cluster_id}/machines")
def clusters_machines_list(
    request: fastapi.Request,
    cluster_id: int | str,
    query: str = "",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    List all cluster machines.
    
    The cluster_id 'all' is a keyword that means all clusters.
    """
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    logger.info(f"{context.rid_get()} cluster '{cluster_id}' query '{query}' try")

    machines_list = []
    machines_map = {} # map machine to cluster
    query_code = 0
    query_result = ""
    query_seconds = 0

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        if cluster_id == "all":
            cluster = None
            clusters_result = services.clusters.list(db_session=db_session, query=query, offset=0, limit=20)
            clusters_list = clusters_result.objects
            app_name = "Machines"
        else:
            cluster = services.clusters.get_by_id_or_name(db_session=db_session, id=cluster_id)
            clusters_list = [cluster]
            app_name = "Cluster Machines"

        for cluster_db in clusters_list:
            list_result = services.machines.list(cluster=cluster_db)

            machines_list.extend(list_result.objects_list)

            for machine in list_result.objects_list:
                machines_map[machine.name] = cluster_db

            query_seconds += list_result.seconds

        query_result = f"query '{query}' returned {len(machines_list)} results in {query_seconds}s"

        logger.info(f"{context.rid_get()} cluster '{cluster_id}' ok")
    except Exception as e:
        query_code = 500
        logger.error(f"{context.rid_get()} clusters '{cluster_id}' exception '{e}'")

    if "HX-Request" in request.headers:
        template = "machines/list_table.html"
    else:
        template = "machines/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": app_name,
                "cluster": cluster,
                "machines_list": machines_list,
                "machines_map": machines_map,
                "prompt_text": "search - e.g. cluster:foo",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} clusters '{cluster_id}' render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response

