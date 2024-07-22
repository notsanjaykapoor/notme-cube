import typing

import sqlmodel

import models

class WorkHandler(typing.Protocol):
    def call(self, db_session: sqlmodel.Session, workq: models.WorkQ) -> int:
        pass