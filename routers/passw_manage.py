import os

import fastapi
import fastapi.responses

import context
import log
import main_shared
import pydantic
import services.passw

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

app_version = os.environ["APP_VERSION"]


class NameStruct(pydantic.BaseModel):
    name: str
    password: str
    user: str | None


@app.get("/passw/orgs/{org}/add", response_class=fastapi.responses.HTMLResponse)
def passw_org_add(
    request: fastapi.Request,
    org: str,
):
    logger.info(f"{context.rid_get()} passw org '{org}' add")

    try:
        response = templates.TemplateResponse(
            request,
            "passw/orgs/add.html",
            {
                "app_name": "Pass",
                "app_version": app_version,
                "org": org,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} passw add render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response


@app.post("/passw/orgs/{org}/create", response_class=fastapi.responses.HTMLResponse)
def passw_org_create(
    request: fastapi.Request,
    name_struct: NameStruct,
    org: str,
):
    logger.info(f"{context.rid_get()} passw org '{org}' create '{name_struct.name}'")

    
    return "ok"