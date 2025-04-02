import dataclasses
import re

import sqlalchemy
import sqlmodel

import models
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.Cluster]
    count: int
    total: int
    errors: list[str]


def list(
    db_session: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20
) -> Struct:
    """
    Search clusters table
    """
    struct = Struct(
        code=0,
        objects=[],
        count=0,
        total=0,
        errors=[],
    )

    model = models.Cluster
    dataset = sqlmodel.select(model)  # default database query

    query_normalized = query

    if query and ":" not in query:
        query_normalized = f"name:{query}"

    struct_tokens = services.mql.parse(query_normalized)

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] == "id":
            dataset = dataset.where(model.id == value)
        elif token["field"] in ["cluster", "name"]:
            # always like query
            value_normal = re.sub(r"~", "", value).lower()
            dataset = dataset.where(
                sqlalchemy.func.lower(model.name).like("%" + value_normal + "%")
            )
        elif token["field"] in ["size_has", "size_has_min"]:
            dataset = dataset.where(model.size_has >= int(value))
        elif token["field"] == "state":
            dataset = dataset.where(model.state == value)

    struct.objects = db_session.exec(dataset.offset(offset).limit(limit).order_by(model.id)).all()
    struct.count = len(struct.objects)
    struct.total = db_session.scalar(
        sqlmodel.select(sqlalchemy.func.count("*")).select_from(dataset.subquery())
    )

    return struct