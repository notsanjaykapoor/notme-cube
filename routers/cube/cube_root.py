import fastapi
import fastapi.responses
import fastapi.templating
import log
import main_shared

import sqlmodel

import services.users


logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/cube", response_class=fastapi.responses.HTMLResponse)
def cube_root(
    request: fastapi.Request,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    cube_options = ["projects", "deploys", "ingress"]

    response = templates.TemplateResponse(
        request,
        "cube/cube_root.html",
        {
            "app_name": "Cube",
            "cube_options": cube_options,
            "user": user,
        }
    )

    return response
