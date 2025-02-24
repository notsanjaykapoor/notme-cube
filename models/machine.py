import dataclasses

CLOUD_GCP = "gcp"
CLOUD_HETZNER = "hetzner"


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
