import os

import contextlib
import dot_init
import fastapi
import fastapi.middleware.cors
import fastapi.staticfiles
import fastapi.templating
import sqlmodel
import starlette.middleware.sessions
import ulid

import context
import log
import main_shared
import routers
import routers.machines
import routers.passw
import routers.users
import routers.workq
import services.database
import services.users

logger = log.init("app")

@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    logger.info("api.startup init")

    # migrate database
    services.database.session.migrate()

    logger.info("api.startup completed")

    yield

# create app object
app = fastapi.FastAPI(lifespan=lifespan)

app_version = os.environ["APP_VERSION"]

app.include_router(routers.machines.machines.app)
app.include_router(routers.passw.passw_list.app)
app.include_router(routers.passw.passw_manage.app)
app.include_router(routers.users.login.app)
app.include_router(routers.users.login_oauth.app)
app.include_router(routers.users.logout.app)
app.include_router(routers.workq.workq.app)

# mount traditional static directory
app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    starlette.middleware.sessions.SessionMiddleware,
    secret_key=os.environ.get("FASTAPI_SESSION_KEY", ""),
    max_age=None,
)

@app.middleware("http")
async def notme_middleware(request: fastapi.Request, call_next):
    # set request id context var
    context.rid_set(ulid.new().str)

    # set user_id context var
    session_id = request.cookies.get("session_id", "")
    if jwt_user := services.users.jwt_token_decode(token=session_id):
        user_id = jwt_user.get("user_id")
    else:
        user_id=0

    context.uid_set(id=user_id)

    response = await call_next(request)
    return response


# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers")


@app.get("/")
def home(
    request: fastapi.Request,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} home")

    if user_id == 0:
        return fastapi.responses.RedirectResponse("/users/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "app_name": "Home",
            "app_version": app_version,
            "user": user,
        }
    )
