import datetime
import typing

import sqlalchemy
import sqlmodel


STATE_DEPLOYED = "deployed"
STATE_DEPLOYING = "deploying"
STATE_ERROR = "error"
STATE_QUEUED = "queued"

STATE_PENDING = "pending" # virtual state
STATES_PENDING = [STATE_DEPLOYING, STATE_QUEUED]

class CubeDeploy(sqlmodel.SQLModel, table=True):
    __tablename__ = "cube_deploys"

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)

    cluster_id: int = sqlmodel.Field(index=True, nullable=False)
    created_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    data: dict = sqlmodel.Field(
        default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON)
    )
    deploy_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True),
    )
    project_name: str = sqlmodel.Field(index=True, nullable=False)
    state: str = sqlmodel.Field(index=True, nullable=False)


    @property
    def state_terminal(self) -> int:
        if self.state in STATES_PENDING:
            return 0
        
        return 1