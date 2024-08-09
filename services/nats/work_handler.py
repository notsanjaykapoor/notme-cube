import asyncio

import sqlmodel

import log
import models

logger = log.init("app")


class WorkHandler:
    async def call(db_session: sqlmodel.Session, workq: models.WorkQ) -> int:
        """
        Called in the context of a work queue worker to process a work object.
        """

        if workq.msg == "sleep":
            seconds = int(workq.data.get("seconds") or 0)
            await asyncio.sleep(seconds)

        return 0