import dataclasses
import time

import models
import services.ssh


@dataclasses.dataclass
class Struct:
    code: int
    container: models.Container
    seconds: int
    errors: list[str]


def start_docker(machine: models.Machine) -> Struct:
    """
    Start docker on the specified machine.
    """
    struct = Struct(
        code=0,
        container=None,
        seconds=0,
        errors=[],
    )

    t1 = time.time()

    cmd_check = "docker info"
    cmd_install = "apt update && apt install -y docker.io"

    struct.code, _ = services.ssh.exec(host=machine.ip, user=machine.user, cmd=cmd_check)

    if struct.code == 0:
        # docker is running
        struct.seconds = round(time.time() - t1, 2)
        return struct

    # install and run docker daemon
    struct.code, ssh_result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=cmd_install)

    if struct.code != 0:
        struct.errors.append(ssh_result)
        return struct

    # verify docker is running

    for loop in [1,2,3]:
        struct.code, ssh_result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=cmd_check)

        if struct.code == 0:
            break

        time.sleep(2)

    if struct.code != 0:
        struct.errors.append(ssh_result)
        return struct

    struct.container = models.Container(
        id="",
        image="",
        name=models.service.SERVICE_DOCKER,
        state=models.container.STATE_RUNNING,
    )

    struct.seconds = round(time.time() - t1, 2)

    return struct

