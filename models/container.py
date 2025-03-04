import dataclasses

STATE_DOWN = "down"
STATE_EXITED = "exited"
STATE_UP = "up"

@dataclasses.dataclass
class Container:
    id: str
    image: str
    name: str
    state: str

    def __str__(self):
        return self.__dict__