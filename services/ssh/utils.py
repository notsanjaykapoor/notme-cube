import json
import subprocess


def exec(host: str, user: str, cmd: str) -> tuple[int, list]:
    response = subprocess.run(
        f"ssh {user}@{host} -o StrictHostKeyChecking=accept-new -t \"{cmd}\"",
        shell=True,
        capture_output=True,
    )

    code = response.returncode

    if code == 0:
        result = response.stdout.decode("utf-8")
    else:
        result = response.stderr.decode("utf-8")
         
    return code, result


def ssh_hosts_remove(host: str) -> tuple[int, list]:
    """
    Remove specified host from local known_hosts file
    """

    response = subprocess.run(
        f"ssh-keygen -R {host}",
        shell=True,
        capture_output=True,
    )

    code = response.returncode

    if code == 0:
        result = response.stdout.decode("utf-8")
    else:
        result = response.stderr.decode("utf-8")
         
    return code, result
