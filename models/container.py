import dataclasses

STATE_EXITED = "exited"
STATE_MISSING = "missing"
STATE_RUNNING = "running"

@dataclasses.dataclass
class Container:
    id: str
    image: str
    name: str
    state: str

    def __str__(self):
        return self.__dict__