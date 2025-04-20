import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.users
import services.daemons


logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/daemons", response_class=fastapi.responses.HTMLResponse)
def daemons_list(
    request: fastapi.Request,
    query: str="",
    offset: int=0,
    limit: int=50,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} daemons list query '{query}'")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        daemons_list_result = services.daemons.list(db_session=db_session, query=query, offset=offset, limit=limit)
        daemons_list = daemons_list_result.objects
        daemons_count = daemons_list_result.total
        query_code = 0
        query_result = f"query '{query}' returned {daemons_count} results"

        logger.info(f"{context.rid_get()} daemons list query '{query}' ok")
    except Exception as e:
        daemons_list = []
        daemons_count = 0
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} daemons list exception '{e}'")


    if "HX-Request" in request.headers:
        template = "daemons/list_table.html"
    else:
        template = "daemons/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Daemons",
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
                "daemons_count": daemons_count,
                "daemons_list": daemons_list,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} daemons render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response
