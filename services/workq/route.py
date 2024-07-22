import models
import services.nats

from .protocol import WorkHandler

handlers = {
    models.workq.QUEUE_WORK : services.nats.WorkHandler
}


def route(queue: str) -> WorkHandler | None:
    """
    """
    return handlers.get(queue)

    