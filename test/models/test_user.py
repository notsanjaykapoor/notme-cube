import pytest
import sqlalchemy.exc
import sqlmodel

import models


def test_user_create(db_session: sqlmodel.Session):
    user_1 = models.User(
        email="user-1@gmail.com",
        idp=models.user.IDP_GOOGLE,
        state=models.user.STATE_ACTIVE,
    )

    db_session.add(user_1)
    db_session.commit()

    assert user_1.id
    assert user_1.email == "user-1@gmail.com"
    assert user_1.idp == "google"
    assert user_1.state == "active"

    # user email is unique

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        user_2 = models.User(
            email=user_1.email,
            idp=models.user.IDP_GOOGLE,
            state=models.user.STATE_ACTIVE,
        )

        db_session.add(user_2)
        db_session.commit()

    db_session.rollback()

    db_session.delete(user_1)
    db_session.commit()


