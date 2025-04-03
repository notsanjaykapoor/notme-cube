import models
import services.nats

from .protocol import WorkHandler

handlers = {
    models.workq.QUEUE_WORK : services.nats.WorkHandler
}


def route(queue: str) -> WorkHandler | None:
    """
    """
    if queue in handlers:
        return handlers.get(queue)()

    return _handler_default()()


def _handler_default() -> WorkHandler:
    return services.nats.WorkHandler
    