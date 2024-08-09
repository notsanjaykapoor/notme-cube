import os

import fastapi
import fastapi.responses
import sqlmodel

import context
import log
import main_shared
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


@app.get("/passw", response_class=fastapi.responses.HTMLResponse)
def passw_orgs_list(
    request: fastapi.Request,
):
    logger.info(f"{context.rid_get()} passw list orgs")

    try:
        list_result = services.passw.orgs_list()
        orgs_list = list_result.orgs
    except Exception as e:
        orgs_list = []
        logger.error(f"{context.rid_get()} passw list orgs exception '{e}'")


    try:
        response = templates.TemplateResponse(
            request,
            "passw/orgs/list.html",
            {
                "app_name": "Pass",
                "app_version": app_version,
                "orgs_list": orgs_list,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} passw list orgs render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response


@app.get("/passw/orgs/{org}", response_class=fastapi.responses.HTMLResponse)
def passw_list(
    request: fastapi.Request,
    org: str,
    query: str="",
    offset: int=0,
    limit: int=50,
):
    logger.info(f"{context.rid_get()} passw list org '{org}' query '{query}'")

    try:
        list_result = services.passw.list(
            org=org,
            query=query,
            offset=offset,
            limit=limit,
        )
        passw_list = list_result.objects
        query_code = 0
        query_result = f"query '{query}' returned {len(passw_list)} results"
    except Exception as e:
        passw_list = []
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} passw exception '{e}'")

    if "HX-Request" in request.headers:
        template = "passw/list_table.html"
    else:
        template = "passw/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Pass",
                "app_version": app_version,
                "org": org,
                "passw_list": passw_list,
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} passw render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response


@app.get("/passw/decrypt", response_class=fastapi.responses.HTMLResponse)
def passw_decrypt(
    request: fastapi.Request,
    org: str,
    name: str,
):
    logger.info(f"{context.rid_get()} passw decrypt org '{org}' name '{name}'")

    try:
        passw = services.passw.get_by_name(org=org, name=name)
        passw = services.passw.decrypt(passw=passw)
    except Exception as e:
        logger.error(f"{context.rid_get()} passw decrypt exception '{e}'")
        passw = None

    try:
        response = templates.TemplateResponse(
            request,
            "passw/list_passw.html",
            {
                "app_name": "Pass",
                "app_version": app_version,
                "org": org,
                "passw": passw
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} passw decrypt render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response


@app.get("/passw/encrypt", response_class=fastapi.responses.HTMLResponse)
def passw_encrypt(
    request: fastapi.Request,
    org: str,
    name: str,
):
    logger.info(f"{context.rid_get()} passw encrypt org '{org}' name '{name}'")

    try:
        passw = services.passw.get_by_name(org=org, name=name)
    except Exception as e:
        logger.error(f"{context.rid_get()} passw encrypt exception '{e}'")
        passw = None

    try:
        response = templates.TemplateResponse(
            request,
            "passw/list_passw.html",
            {
                "app_name": "Pass",
                "app_version": app_version,
                "org": org,
                "passw": passw
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} passw encrypt render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})
    
    return response
