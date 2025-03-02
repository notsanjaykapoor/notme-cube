import sqlmodel

import models


def delete(db_session: sqlmodel.Session, cluster: models.Cluster) -> int:
    if not cluster:
        return 404

    if cluster.deletable == 0:
        return 422

    db_session.delete(cluster)
    db_session.commit()

    return 0
