from .connect import connect
from .utils import msg_decode, msg_encode
from .work_handler import WorkHandler

NATS_MSG_PONG = "workers.pong"
NATS_MSG_SHUTDOWN = "workers.shutdown"
NATS_MSG_STATUS = "workers.status"
