import os
import secrets

import fastapi
import fastapi.responses
import fastapi.templating

import context
import log
import main_shared
import pydantic

import services.passw

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


class PasswStruct(pydantic.BaseModel):
    name: str
    password: str
    user: str | None


@app.get("/passw/orgs/{org}/new", response_class=fastapi.responses.HTMLResponse)
def passw_org_add(
    request: fastapi.Request,
    org: str,
):
    logger.info(f"{context.rid_get()} passw org '{org}' new")

    try:
        response = templates.TemplateResponse(
            request,
            "passw/orgs/new.html",
            {
                "app_name": "Pass",
                "org": org,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} passw org '{org}' new render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response


@app.post("/passw/orgs/{org}/create", response_class=fastapi.responses.JSONResponse)
def passw_org_create(
    request: fastapi.Request,
    passw_struct: PasswStruct,
    org: str,
):
    logger.info(f"{context.rid_get()} passw org '{org}' create '{passw_struct.name}'")

    crypt_struct = services.passw.encrypt(password=passw_struct.password, user=passw_struct.user)

    dir_uri= os.environ.get("PASS_DIR_URI")
    _source_host, source_dir, _ = services.passw.file_uri_parse(source_uri=dir_uri)

    file_path = f"{source_dir}{org}/{passw_struct.name}.gpg"

    with open(file_path, "wb") as f:
        f.write(crypt_struct.data)

    logger.info(f"{context.rid_get()} passw org '{org}' create file '{file_path}' ok")

    response = fastapi.responses.JSONResponse(content={"response": "ok"})
    response.headers["HX-Redirect"] = f"/passw/orgs/{org}"

    return response


@app.get("/passw/orgs/{org}/generate", response_class=fastapi.responses.JSONResponse)
def passw_org_generate(
    request: fastapi.Request,
    org: str,
):
    logger.info(f"{context.rid_get()} passw org '{org}' generate")

    password = secrets.token_urlsafe(13)

    response = templates.TemplateResponse(
        request,
        "passw/orgs/new_password.html",
        {
            "app_name": "Pass",
            "password": password,
        }
    )

    return response
