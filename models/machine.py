import dataclasses

CLOUD_GCP = "gcp"
CLOUD_HETZNER = "hetzner"

# hetzner server states
STATE_DELETING = "deleting"
STATE_INITIALIZING = "initializing"
STATE_MIGRATING = "migrating"
STATE_OFF = "off"
STATE_REBUILDING = "rebuilding"
STATE_RUNNING = "running"
STATE_STARTING = "starting"
STATE_STOPPING = "stopping"
STATE_UNKNOWN = "unknown"

STATES_UP = [STATE_INITIALIZING, STATE_RUNNING, STATE_STARTING]


@dataclasses.dataclass
class Machine:
    cloud: str
    id: str
    image: str
    ip: str
    location: str
    name: str
    state: str
    tags: dict
    type: str

    apps: int = 0
    containers: int = 0
    user: str = ""

    def __str__(self):
        return self.__dict__

    @property
    def cluster(self) -> str:
        return self.tags.get("cluster") or ""

    @property
    def protected(self) -> int:
        # defaults to 0 which means not protected
        return self.tags.get("protected") or 0

    @property
    def services(self) -> str:
        return self.tags.get("services") or ""
