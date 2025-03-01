import re
import typing

import sqlmodel

import models


def get_by_id_or_name(db_session: sqlmodel.Session, id: int|str) -> typing.Optional[models.Cluster]:
    if re.search(r"^\d+$", str(id)):
        return get_by_id(db_session, id)
    else:
        return get_by_name(db_session, id)


def get_by_id(db_session: sqlmodel.Session, id: int) -> typing.Optional[models.Cluster]:
    db_select = sqlmodel.select(models.Cluster).where(models.Cluster.id == id)
    db_object = db_session.exec(db_select).first()

    return db_object


def get_by_name(db_session: sqlmodel.Session, name: str) -> typing.Optional[models.Cluster]:
    db_select = sqlmodel.select(models.Cluster).where(models.Cluster.name == name)
    db_object = db_session.exec(db_select).first()

    return db_object