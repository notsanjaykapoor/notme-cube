import subprocess


def check(ip: str, port: int=4222) -> int:
    cmd = f"nats server check connection -s nats://{ip}:{port}"
    response = subprocess.run(cmd, shell=True, capture_output=True)

    return response.returncode
