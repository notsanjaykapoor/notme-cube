import datetime
import pytz
import typing

import sqlalchemy
import sqlmodel


STATE_RUNNING = "running"
STATE_SHUTDOWN = "shutdown"
STATE_STARTUP = "startup"

STATE_ACTIVE = "active" # virtual state
STATES_ACTIVE = [STATE_RUNNING, STATE_STARTUP]


class Daemon(sqlmodel.SQLModel, table=True):
    __tablename__ = "daemons"
    __table_args__ = (
        sqlalchemy.UniqueConstraint("name", "service", name="_daemons_name_service"),
    )

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)

    created_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
        ),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    data: dict = sqlmodel.Field(
        default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON)
    )
    name: str = sqlmodel.Field(index=True, nullable=False)
    service: str = sqlmodel.Field(index=True, nullable=False)
    state: str = sqlmodel.Field(index=True, nullable=False)
    updated_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            onupdate=sqlalchemy.sql.func.now(),
        ),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )

    @property
    def active(self) -> int:
        if self.state in STATES_ACTIVE:
            return 1
        
        return 0

    def last_timestamp(self, tz="") -> str:
        time_at_tz = self.updated_at.replace(tzinfo=pytz.utc)

        if tz:
            time_at_tz = time_at_tz.astimezone(pytz.timezone(tz))

        return time_at_tz.strftime(self.time_format)
    
    @property
    def time_format(self) -> str:
        return "%Y-%m-%d at %H:%M:%S%z"
