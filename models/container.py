import dataclasses

@dataclasses.dataclass
class Container:
    id: str
    image: str
    name: str

    def __str__(self):
        return self.__dict__