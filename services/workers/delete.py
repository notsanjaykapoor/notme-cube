import sqlmodel

import services.workers


def delete_by_name(db_session: sqlmodel.Session, name: str) -> int:
    worker = services.workers.get_by_name(db_session=db_session, name=name)

    if not worker:
        return 404

    db_session.delete(worker)
    db_session.commit()

    return 0
