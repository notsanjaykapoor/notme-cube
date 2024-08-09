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
import services.database

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

app.include_router(routers.machines.app)
app.include_router(routers.passw.app)
app.include_router(routers.workq.app)

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
    secret_key=os.environ.get("FASTAPI_SESSION_KEY"),
    max_age=None,
)

@app.middleware("http")
async def add_request_id(request: fastapi.Request, call_next):
    # set request id context var
    context.rid_set(ulid.new().str)
    response = await call_next(request)
    return response


@app.get("/")
def home():
    return fastapi.responses.RedirectResponse("/machines")