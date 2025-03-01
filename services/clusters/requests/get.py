import typing

import sqlmodel

import models


def get_pending_any(db_session: sqlmodel.Session) -> typing.Optional[models.ClusterRequest]:
    db_select = sqlmodel.select(models.ClusterRequest).where(
        models.ClusterRequest.state.in_(models.cluster_request.STATES_PENDING),
    )
    db_object = db_session.exec(db_select).first()

    return db_object


def get_pending_by_cluster_id(db_session: sqlmodel.Session, cluster_id: int) -> typing.Optional[models.ClusterRequest]:
    db_select = sqlmodel.select(models.ClusterRequest).where(
        models.ClusterRequest.state.in_(models.cluster_request.STATES_PENDING),
    ).where(
        models.ClusterRequest.cluster_id == cluster_id
    )
    db_object = db_session.exec(db_select).first()

    return db_object


def get_processing_all(db_session: sqlmodel.Session) -> list[models.ClusterRequest]:
    db_select = sqlmodel.select(models.ClusterRequest).where(
        models.ClusterRequest.state == models.cluster_request.STATE_PROCESSING,
    )
    return db_session.exec(db_select).all()
