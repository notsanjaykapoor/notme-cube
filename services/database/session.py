import os

import sqlalchemy
import sqlmodel

import dot_init # noqa: F401

database_url = os.environ.get("DATABASE_URL")

assert database_url

connect_args: dict = {}

engine = sqlmodel.create_engine(database_url, echo=False, connect_args=connect_args)


# create and migrate db tables
def migrate():
    sqlmodel.SQLModel.metadata.create_all(engine)


# get session object
def get() -> sqlmodel.Session:
    return sqlmodel.Session(engine)


def table_names() -> list[str]:
    return sqlalchemy.inspect(engine).get_table_names()