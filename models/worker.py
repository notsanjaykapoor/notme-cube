import datetime

import sqlmodel


STATE_BUSY = "busy"
STATE_IDLE = "idle"


class Worker(sqlmodel.SQLModel, table=True):
    __tablename__ = "workers"

    id: int | None = sqlmodel.Field(default=None, primary_key=True)

    created_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)
    data: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    name: str = sqlmodel.Field(index=False, nullable=False, max_length=50)
    state: str = sqlmodel.Field(index=False, nullable=True, max_length=50, default="")
    updated_at: datetime.datetime = sqlmodel.Field(default_factory=datetime.datetime.utcnow, nullable=False)
