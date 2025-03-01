import datetime
import typing

import sqlalchemy
import sqlmodel


STATE_COMPLETED = "completed"
STATE_ERROR = "error"
STATE_PROCESSING = "processing"
STATE_QUEUED = "queued"

STATE_PENDING = "pending" # virtual state
STATES_PENDING = [STATE_PROCESSING, STATE_QUEUED]

class ClusterRequest(sqlmodel.SQLModel, table=True):
    __tablename__ = "cluster_requests"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)

    cluster_id: int = sqlmodel.Field(index=False, nullable=False)
    created_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    data: dict = sqlmodel.Field(
        default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON)
    )
    size_ask: int = sqlmodel.Field(index=False, nullable=False)
    size_has: int = sqlmodel.Field(index=False, nullable=False)
    state: str = sqlmodel.Field(index=True, nullable=False)


    @property
    def machine_name(self) -> str:
        return self.data.get("machine_name") or ""

    @property
    def name(self) -> str:
        if self.size_ask > self.size_has:
            return "up"
        else:
            return "down"
