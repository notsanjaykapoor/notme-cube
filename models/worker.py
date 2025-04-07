import datetime

import sqlmodel

HEARTBEAT_STALE_SECS = 60

STATE_BUSY = "busy"
STATE_IDLE = "idle"
STATE_TERM = "term"

STATES_ACTIVE = [STATE_BUSY, STATE_IDLE]


class Worker(sqlmodel.SQLModel, table=True):
    __tablename__ = "workers"

    id: int | None = sqlmodel.Field(default=None, primary_key=True)

    created_at: datetime.datetime = sqlmodel.Field(default_factory=lambda: datetime.datetime.now(datetime.UTC), nullable=False)
    data: dict = sqlmodel.Field(default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON))
    name: str = sqlmodel.Field(index=False, nullable=False, max_length=50)
    state: str = sqlmodel.Field(index=False, nullable=True, max_length=50, default="")
    updated_at: datetime.datetime = sqlmodel.Field(default_factory=lambda: datetime.datetime.now(datetime.UTC), nullable=False)
