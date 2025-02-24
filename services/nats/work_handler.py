import asyncio
import math

import sqlmodel

import log
import models

logger = log.init("app")


class WorkHandler:
    async def call(self, db_session: sqlmodel.Session, job: models.WorkQ) -> int:
        """
        Called in the context of a work queue worker to process a work object.
        """

        if job.msg == "sleep":
            seconds = int(job.data.get("seconds") or 0)
            await self._sleep(seconds)

        return 0
    

    async def _sleep(self, seconds: int) -> int:
        """
        """
        if seconds == 0:
            return 0
        
        if seconds <= 2:
            await asyncio.sleep(seconds)
            return 0

        # break sleep into chunks
        base = math.floor(seconds / 3)
        rem = seconds % 3
        loops = [base, base, base, rem]

        for count in loops:
            print("sleep", count)
            await asyncio.sleep(count)

        return 0
        
