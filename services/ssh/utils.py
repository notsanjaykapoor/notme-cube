import subprocess
import time

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


def verify(host: str, user: str, retries: int) -> tuple[int, list]:
    """
    Verify ssh connection to specified host is working
    """
    count = 0

    while count < retries:
        code, result = exec(host=host, user=user, cmd="ls")

        if code == 0:
            break

        time.sleep(2)

        if code == 255:
            # clear hosts file first, then run command again
            ssh_hosts_remove(host=host)

        count += 1

    return code, result

