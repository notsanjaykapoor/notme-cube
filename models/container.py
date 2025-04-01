import dataclasses

STATE_DOWN = "down"
STATE_EXITED = "exited"
STATE_RUNNING = "running"

@dataclasses.dataclass
class Container:
    id: str
    image: str
    name: str
    state: str

    ports: str=""
    networks: str=""
    uptime: str=""

    def __str__(self):
        return self.__dict__