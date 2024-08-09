import json


def msg_decode(b: bytes) -> dict:
    return json.loads(b.decode())


def msg_encode(d: dict) -> bytes:
    return json.dumps(d).encode()