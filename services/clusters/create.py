import sqlmodel

import models


def create(db_session: sqlmodel.Session, name: str) -> models.Cluster:
    cluster = models.Cluster(
        data={
            "cloud": models.cluster.CLOUD_DEFAULT,
            "server_image": models.cluster.SERVER_IMAGE_DEFAULT,
            "server_location": models.cluster.SERVER_LOC_DEFAULT,
            "server_type": models.cluster.SERVER_TYPE_DEFAULT,
        },
        name=name,
        size_ask=0,
        size_has=0,
        state=models.cluster.STATE_ACTIVE,
    )

    db_session.add(cluster)
    db_session.commit()

    return cluster
