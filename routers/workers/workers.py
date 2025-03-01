import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import models
import services.users
import services.workers
import services.workq


logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/workers", response_class=fastapi.responses.HTMLResponse)
def workers_list(
    request: fastapi.Request,
    query: str="",
    offset: int=0,
    limit: int=50,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} workers list query '{query}'")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    try:
        workers_list_result = services.workers.list(db_session=db_session, query=query, offset=offset, limit=limit)
        worker_objects = workers_list_result.objects
        workers_count = workers_list_result.total
        query_code = 0
        query_result = f"query '{query}' returned {workers_list_result.total} results"

        backlog_count = services.workq.count_queued(db_session=db_session, queue=models.workq.QUEUE_WORK)

        logger.info(f"{context.rid_get()} workers list query '{query}' ok")
    except Exception as e:
        backlog_count = 0
        worker_objects = []
        workers_count = 0
        query_code = 400
        query_result = f"exception {e}"
        logger.error(f"{context.rid_get()} workers list exception '{e}'")


    if "HX-Request" in request.headers:
        template = "workers/list_table.html"
    else:
        template = "workers/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Workers",
                "backlog_count": backlog_count,
                "prompt_text": "search",
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
                "workers_count": workers_count,
                "worker_objects": worker_objects,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} workers render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    if "HX-Request" in request.headers:
        response.headers["HX-Push-Url"] = f"{request.get('path')}?query={query}"

    return response


@app.get("/workers/{worker_name}/shutdown", response_class=fastapi.responses.HTMLResponse)
def workers_shutdown(
    request: fastapi.Request,
    worker_name: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} worker '{worker_name}' shutdown")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    http_referer = request.headers.get("referer")

    try:
        # add shutdown message to workq
        services.workers.shutdown(
            db_session=db_session,
            queue=models.workq.QUEUE_WORK,
            sender=f"user-{user.id}",
            worker_name=worker_name,
        )

        # redirect to workq list
        http_referer = "/workq"

        logger.info(f"{context.rid_get()} worker '{worker_name}' shutdown ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} worker '{worker_name}' shutdown exception '{e}'")


    return fastapi.responses.RedirectResponse(http_referer)
