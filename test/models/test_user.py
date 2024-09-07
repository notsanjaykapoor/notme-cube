import sqlmodel

import models


def test_user_create(db_session: sqlmodel.Session):
    user = models.User(
        email="user-1@gmail.com",
        idp=models.user.IDP_GOOGLE,
        state=models.user.STATE_ACTIVE,
    )

    db_session.add(user)
    db_session.commit()

    assert user.id
    assert user.email == "user-1@gmail.com"
    assert user.idp == "google"
    assert user.state == "active"

    db_session.delete(user)
    db_session.commit()
