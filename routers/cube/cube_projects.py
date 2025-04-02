import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.users
import services.cube
import services.cube.pods
import services.cube.projects


logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

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
