import os

import contextlib
import dot_init
import fastapi
import fastapi.middleware.cors
import fastapi.staticfiles
import fastapi.templating
import starlette.middleware.sessions
import ulid

import context
import log
import routers
import routers.machines
import routers.passw
import routers.users
import routers.workq
import services.database
import services.users

logger = log.init("api")

@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    logger.info("api.startup init")

    # migrate database
    services.database.session.migrate()

    logger.info("api.startup completed")

    yield

# create app object
app = fastapi.FastAPI(lifespan=lifespan)

app.include_router(routers.machines.machines.app)
app.include_router(routers.passw.passw_list.app)
app.include_router(routers.passw.passw_manage.app)
app.include_router(routers.users.login.app)
app.include_router(routers.users.login_oauth.app)
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


@app.get("/")
def home():
    return fastapi.responses.RedirectResponse("/machines")