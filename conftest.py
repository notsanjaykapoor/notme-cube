import os

import pytest
import sqlalchemy
import sqlalchemy.future
import sqlmodel
import sqlmodel.pool

import dot_init  # noqa: F401
import models
import services.clusters
import services.database
import services.users

# set app env vars
os.environ["APP_ENV"] = "tst"
os.environ["CUBE_CONFIG_PATH"] = "file://localhost//Users/sanjaykapoor/notme/notme-cube/test/data/cube_config.yml"

test_db_name = os.environ.get("DATABASE_TEST_URL")
connect_args: dict = {}

assert test_db_name

if "sqlite" in test_db_name:
    # sqlite specific
    connect_args = {"check_same_thread": False}

engine = sqlmodel.create_engine(
    test_db_name,
    connect_args=connect_args,
    poolclass=sqlmodel.pool.StaticPool,
)


def database_tables_create(engine: sqlalchemy.future.Engine):
    sqlmodel.SQLModel.metadata.create_all(engine)


def database_tables_drop(engine: sqlalchemy.future.Engine):
    sqlmodel.SQLModel.metadata.drop_all(engine)


# Set up the database once
database_tables_drop(engine)
database_tables_create(engine)


@pytest.fixture(name="db_session")
def session_fixture():
    connection = engine.connect()
    transaction = connection.begin()

    # begin a nested transaction (using SAVEPOINT)
    nested = connection.begin_nested()

    session = sqlmodel.Session(engine)

    # if the application code calls session.commit, it will end the nested transaction
    # when that happens, start a new one.
    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    # yield session to test
    yield session

    session.close()

    # rollback the overall transaction, restoring the state before the test ran
    transaction.rollback()
    connection.close()


@pytest.fixture(name="cluster_1")
def cluster_1_fixture(db_session: sqlmodel.Session):
    cluster = services.clusters.create(
        db_session=db_session,
        name="cluster-1",
        services="test",
    )

    db_session.add(cluster)
    db_session.commit()

    assert cluster.id

    yield cluster

    services.database.truncate_tables(db_session=db_session, table_names=["clusters"])


@pytest.fixture(name="machine_1")
def machine_1_fixture():
    machine = models.Machine(
        cloud=models.machine.CLOUD_HETZNER,
        id="id",
        image="image",
        ip="0.0.0.0",
        location="location",
        name="machine-1",
        state=models.machine.STATE_RUNNING,
        tags={},
        type="type",
        user=os.environ.get("VPS_HETZNER_USER"),
    )

    yield machine


@pytest.fixture(name="project_1")
def project_1_fixture():
    project = models.CubeProject(
        name="project-1",
        dir="/tmp"
    )

    yield project


@pytest.fixture(name="user_1")
def user_1_fixture(db_session: sqlmodel.Session):
    user = models.User(
        email="user-1@gmail.com",
        idp=models.user.IDP_GOOGLE,
        state=models.user.STATE_ACTIVE,
    )

    db_session.add(user)
    db_session.commit()

    assert user.id

    yield user

    services.database.truncate_tables(db_session=db_session, table_names=["users"])
