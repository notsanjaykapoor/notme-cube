import dataclasses

STATE_DOWN = "down"
STATE_HEALTHY = "healthy"

@dataclasses.dataclass
class CloudflareIngress:
    hostname: str
    path: str
    service: str
    tunnel_id: str
    tunnel_name: str
    tunnel_status: str

    def __str__(self):
        return self.__dict__