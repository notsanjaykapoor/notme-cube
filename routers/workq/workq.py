import os

import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import models
import services.users
import services.workq
import services.workers


logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/workq", response_class=fastapi.responses.HTMLResponse)
def workq_list(
    request: fastapi.Request,
    query: str="",
    offset: int=0,
    limit: int=50,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} workq list query '{query}'")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        wq_list_result = services.workq.list(db_session=db_session, query=query, offset=offset, limit=limit)
        workq_objects = wq_list_result.objects
        query_code = 0
        query_result = f"query '{query}' returned {wq_list_result.total} results"

        workers_query = "state:active"
        workers_list_result = services.workers.list(db_session=db_session, query=workers_query, offset=offset, limit=limit)
        workers_count = len(workers_list_result.objects)

        backlog_count = services.workq.count_queued_all(db_session=db_session)

        logger.info(f"{context.rid_get()} workq list query '{query}' ok")
    except Exception as e:
        backlog_count = 0
        workq_objects = []
        workers_count = 0
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} workq list exception '{e}'")

    if "HX-Request" in request.headers:
        template = "workq/list_table.html"
    else:
        template = "workq/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "WorkQ",
                "backlog_count": backlog_count,
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
                "workers_count": workers_count,
                "workq_objects": workq_objects,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} workq render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response