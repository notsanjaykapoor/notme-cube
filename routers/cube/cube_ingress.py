import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.users
import services.cf.ingress


logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/ingress", response_class=fastapi.responses.HTMLResponse)
def cube_ingress_list(
    request: fastapi.Request,
    query: str="",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} cube ingress list query '{query}'")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        list_result = services.cf.ingress.list(query=query)
        ingress_list = list_result.ingress_list
        query_code = 0
        query_result = f"query '{query}' returned {len(ingress_list)} results"

        logger.info(f"{context.rid_get()} cube ingress list query '{query}' ok - {len(ingress_list)} objects")
    except Exception as e:
        ingress_list = []
        query_code = 500
        query_result = ""
        logger.error(f"{context.rid_get()} cube ingress list exception '{e}'")

    if "HX-Request" in request.headers:
        template = "cube/ingress/list_table.html"
    else:
        template = "cube/ingress/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Cube Ingress",
                "ingress_list": ingress_list,
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
