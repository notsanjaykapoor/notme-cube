import time

import sqlmodel

import log
import models

logger = log.init("app")


class WorkHandler:
    def call(db_session: sqlmodel.Session, workq: models.WorkQ) -> int:
        """
        Called in the context of a work queue worker to process a work object.
        """

        if workq.msg == "sleep":
            time.sleep(workq.data.get("seconds"))

        return 0