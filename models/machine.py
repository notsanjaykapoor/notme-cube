import dataclasses

CLOUD_GCP = "gcp"
CLOUD_HETZNER = "hetzner"


@dataclasses.dataclass
class Machine:
    cloud: str
    id: str
    ip: str
    name: str
    state: str

    apps: int = 0
    containers: int = 0
    user: str = ""

    def __str__(self):
        return self.__dict__