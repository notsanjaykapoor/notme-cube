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


@app.get("/cube/projects/{project_name}/pods", response_class=fastapi.responses.HTMLResponse)
def cube_pods_list(
    request: fastapi.Request,
    project_name: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} cube project '{project_name}' pods")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        projects_result = services.cube.projects.list(path=services.cube.config_path(), query=project_name)
        project = projects_result.projects[0]

        pods_result = services.cube.pods.list(projects=[project])
        pods_list = pods_result.pods
    except Exception as e:
        logger.info(f"{context.rid_get()} cube project '{project_name}' pods exception - {e}")

    try:
        response = templates.TemplateResponse(
            request,
            "cube/pods/list.html",
            {
                "app_name": "Cube Project Pods",
                "pods_list": pods_list,
                "project": project,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} cube project '{project_name}' render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
