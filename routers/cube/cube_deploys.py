import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.users
import services.clusters
import services.cube
import services.cube.deploys
import services.cube.projects


logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(
    directory="routers",
    context_processors=[main_shared.jinja_context],
)

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

@app.get("/cube/deploy/projects/{project_name}", response_class=fastapi.responses.HTMLResponse)
def cube_deploys_create(
    request: fastapi.Request,
    project_name: str,
    cluster_id: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} cube deploy project '{project_name}' cluster '{cluster_id}'")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    cluster = services.clusters.get_by_id_or_name(db_session=db_session, id=cluster_id)

    projects_result = services.cube.projects.list(path=services.cube.config_path(), query=f"name:{project_name}")
    project = projects_result.projects[0]

    referer_path = request.headers.get("referer")

    if not cluster or not project:
        logger.error(f"{context.rid_get()} cube deploy project '{project_name}' cluster '{cluster_id}' - invalid project or cluster")
        return fastapi.responses.RedirectResponse(referer_path)

    create_result = services.cube.deploys.create(
        db_session=db_session,
        cluster=cluster,
        project=project,
    )

    logger.info(f"{context.rid_get()} cube deploy project '{project_name}' cluster '{cluster_id}' ok - deploy id '{create_result.deploy.id}")

    return fastapi.responses.RedirectResponse(referer_path)


@app.get("/cube/deploys", response_class=fastapi.responses.HTMLResponse)
def cube_deploys_list(
    request: fastapi.Request,
    query: str="",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} cube deploys list")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        deploys_result = services.cube.deploys.list(
            db_session=db_session,
            query=query,
            offset=0,
            limit=20,
            sort="id-",
        )
        deploys_list = deploys_result.objects

        clusters_result = services.clusters.list(
            db_session=db_session,
            query="",
            offset=0,
            limit=10,
        )
        clusters_list = clusters_result.objects

        query_code = 0
        query_result = f"query '{query}' returned {len(deploys_list)} results"
    except Exception as e:
        deploys_list = []
        clusters_list =[]
        query_code = 500
        query_result = ""
        logger.info(f"{context.rid_get()} cube deploys list exception - {e}")

    clusters_map = {cluster.id:cluster.name for cluster in clusters_list}

    if "HX-Request" in request.headers:
        template = "cube/deploys/list_table.html"
    else:
        template = "cube/deploys/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Cube Deploys",
                "deploys_list": deploys_list,
                "clusters_map": clusters_map,
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} cube deploys list render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response
