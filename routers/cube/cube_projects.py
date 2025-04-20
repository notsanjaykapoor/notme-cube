import fastapi
import fastapi.responses
import fastapi.templating
import sqlalchemy
import sqlmodel

import context
import log
import main_shared
import services.users
import services.cube
import services.cube.deploys
import services.cube.pods
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


@app.get("/cube/projects", response_class=fastapi.responses.HTMLResponse)
def cube_projects_list(
    request: fastapi.Request,
    query: str="",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    List cube projects.
    """
    logger.info(f"{context.rid_get()} cube projects list query '{query}'")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    cube_path = services.cube.config_path()

    try:
        list_result = services.cube.projects.list(path=cube_path, query=query)
        projects_list = list_result.projects
        query_code = 0
        query_result = f"query '{query}' returned {len(projects_list)} results"

        clusters_result = services.clusters.list(db_session=db_session, query="size_has_min:1", offset=0, limit=10)
        clusters_list = clusters_result.objects

        # get deploy count by project
        db_result = db_session.exec(
            sqlalchemy.text("select project_name, count(id) from cube_deploys group by project_name")
        ).all()
        projects_deploys_count = {
            tuple[0]:tuple[1] for tuple in db_result
        }

        logger.info(f"{context.rid_get()} cube projects list query '{query}' ok - {len(projects_list)} projects")
    except Exception as e:
        projects_list = []
        clusters_list = []
        query_code = 500
        query_result = ""
        logger.error(f"{context.rid_get()} cube projects list exception '{e}'")

    if "HX-Request" in request.headers:
        template = "cube/projects/list_table.html"
    else:
        template = "cube/projects/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Cube Projects",
                "clusters_list": clusters_list,
                "cube_path": cube_path,
                "projects_deploys_count": projects_deploys_count,
                "projects_list": projects_list,
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} cube projects render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response



@app.get("/cube/projects/{project_name}", response_class=fastapi.responses.HTMLResponse)
def cube_projects_show(
    request: fastapi.Request,
    project_name: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    Cube project show view.
    """
    logger.info(f"{context.rid_get()} cube project '{project_name}' try")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    cube_path = services.cube.config_path()

    try:
        projects_result = services.cube.projects.list(path=services.cube.config_path(), query=project_name)
        project = projects_result.projects[0]

        pods_result = services.cube.pods.list(projects=[project])
        pods_list = pods_result.pods

        deploys_result = services.cube.deploys.list(
            db_session=db_session,
            query=f"project:{project_name}",
            offset=0,
            limit=20,
            sort="id-",
        )
        deploys_list = deploys_result.objects
        deploys_total = deploys_result.total

        # map deploys by cluster, so we can identify the most recent deploy in a terminal state
        deploys_map_by_cluster = {}
        for deploy in deploys_list:
            if deploy.cluster_id not in deploys_map_by_cluster:
                deploys_map_by_cluster[deploy.cluster_id] = []

            if len(deploys_map_by_cluster[deploy.cluster_id]) == 0:
                if deploy.state_terminal == 0:
                    # most recent deploy in cluster is pending, mark the cluster to prevent new deploys
                    deploys_map_by_cluster[deploy.cluster_id].append(0)
                else:
                    # most recent deploy in cluster is in a terminal state
                    deploys_map_by_cluster[deploy.cluster_id].append(deploy.id)
 
        clusters_result = services.clusters.list(
            db_session=db_session,
            query="",
            offset=0,
            limit=10,
        )
        clusters_list = clusters_result.objects

        # map cluster id to name
        clusters_map = {
            cluster.id:cluster.name for cluster in clusters_list
        }

        logger.info(f"{context.rid_get()} cube project '{project_name}' ok")
    except Exception as e:
        logger.info(f"{context.rid_get()} cube project '{project_name}' pods exception - {e}")

    if "HX-Request" in request.headers:
        template = ""
    else:
        template = "cube/projects/show.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Cube Project",
                "clusters_list": clusters_list,
                "clusters_map": clusters_map,
                "cube_path": cube_path,
                "deploys_list": deploys_list,
                "deploys_map_by_cluster": deploys_map_by_cluster,
                "deploys_total": deploys_total,
                "pods_list": pods_list,
                "project": project,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} cube projects render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
