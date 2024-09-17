import os

import fastapi
import fastapi.responses
import fastapi.templating

import context
import log
import main_shared
import pydantic

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


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