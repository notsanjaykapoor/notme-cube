import dataclasses

import models
import services.scp
import services.ssh


@dataclasses.dataclass
class Struct:
    code: int
    container: models.Container
    seconds: int
    errors: list[str]


def start_service(machine: models.Machine, service: str) -> Struct:
    """
    Make sure container 'service' is running on the specified machine.
    """
    struct = Struct(
        code=0,
        container=None,
        seconds=0,
        errors=[],
    )

    # get service config

    service_dict = models.service.get(service)

    if not service_dict:
        struct.code = 404
        return struct

    # ssh cmds first

    for cmd in service_dict.get("ssh_cmds"):
        struct.code, result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=cmd)

        if struct.code != 0:
            struct.errors.append(result)
            return struct

    # scp cmds next

    for file_tuple in service_dict.get("scp_files"):
        struct.code, result = services.scp.exec(host=machine.ip, user=machine.user, src=file_tuple[0], dst=file_tuple[1])

        if struct.code != 0:
            struct.errors.append(result)
            return struct

    # pull docker image

    docker_image = service_dict.get('docker_image')
    docker_pull_cmd = f"docker pull {docker_image}"

    struct.code, result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=docker_pull_cmd)

    if struct.code != 0:
        struct.errors.append(result)
        return struct

    # start container with updated entrypoint

    docker_entrypoint = service_dict.get('docker_entrypoint').replace("$cluster", machine.cluster)
    docker_run_cmd = f"{service_dict.get('docker_run')} {docker_image} {docker_entrypoint}"

    struct.code, ssh_result = services.ssh.exec(host=machine.ip, user=machine.user, cmd=docker_run_cmd)

    if struct.code != 0:
        struct.errors.append(ssh_result)
        return struct

    struct.container = models.Container(
        id="",
        image=docker_image,
        name=service,
        state=models.container.STATE_RUNNING,
    )

    return struct