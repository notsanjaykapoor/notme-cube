import dataclasses

import sqlalchemy
import sqlmodel

import models
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.ClusterRequest]
    count: int
    total: int
    errors: list[str]


def list(
    db_session: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20
) -> Struct:
    """
    Search cluster requests table
    """
    struct = Struct(
        code=0,
        objects=[],
        count=0,
        total=0,
        errors=[],
    )

    model = models.ClusterRequest
    dataset = sqlmodel.select(model)  # default database query

    query_normalized = query

    # if query and ":" not in query:
    #     query_normalized = f"name:{query}"

    struct_tokens = services.mql.parse(query_normalized)

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] == "cluster_id":
            dataset = dataset.where(model.cluster_id == value)
        elif token["field"] == "id":
            dataset = dataset.where(model.id == value)
        elif token["field"] == "state":
            if value == models.cluster_request.STATE_PENDING:
                dataset = dataset.where(model.state.in_(models.cluster_request.STATES_PENDING))
            else:
                dataset = dataset.where(model.state == value)

    struct.objects = db_session.exec(dataset.offset(offset).limit(limit).order_by(model.id.desc())).all()
    struct.count = len(struct.objects)
    struct.total = db_session.scalar(
        sqlmodel.select(sqlalchemy.func.count("*")).select_from(dataset.subquery())
    )

    return struct