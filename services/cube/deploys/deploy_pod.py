import dataclasses
import os
import subprocess

import context
import log
import models
import services.cube.pods
import services.hetzner.servers

@dataclasses.dataclass
class Struct:
    code: int
    errors: list[str]


def deploy_pod(project: models.CubeProject, pod: models.CubePod, cluster: models.Cluster) -> Struct:
    """
    Deploy a pod (container) to a cluster.
    """
    struct = Struct(
        code=0,
        errors=[],
    )

    logger = log.init("app")

    servers_struct = services.hetzner.servers.list(query=f"cluster:{cluster.name}")
    machines_list = servers_struct.objects_list

    if len(machines_list) == 0:
        raise Exception("machine not available")

    if len(machines_list) > 1:
        raise Exception("machine must be specified")
    
    machine = machines_list[0]

    logger.info(f"{context.rid_get()} deploy pod '{project.name}/{pod.c_name}' machine '{cluster.name}/{machine.name}' try")

    struct.code, error = _machine_scp(machine=machine, project=project, pod=pod)

    if struct.code != 0:
        logger.error(f"{context.rid_get()} deploy pod '{project.name}/{pod.c_name}' machine '{cluster.name}/{machine.name}' scp error {struct.code} - {error}")
        return struct

    logger.info(f"{context.rid_get()} deploy pod '{project.name}/{pod.c_name}' machine '{cluster.name}/{machine.name}' scp ok")

    struct.code, error = _machine_docker_stop(machine=machine, pod=pod)

    if struct.code != 0:
        logger.error(f"{context.rid_get()} deploy pod '{project.name}/{pod.c_name}' machine '{cluster.name}/{machine.name}' docker stop error {struct.code} - {error}")
        return struct

    struct.code, error = _machine_docker_start(machine=machine, pod=pod)

    if struct.code != 0:
        logger.error(f"{context.rid_get()} deploy pod '{project.name}/{pod.c_name}' machine '{cluster.name}/{machine.name}' docker start error {struct.code} - {error}")
        return struct

    logger.info(f"{context.rid_get()} deploy pod '{project.name}/{pod.c_name}' machine '{cluster.name}/{machine.name}' docker ok")

    return struct


def _machine_docker_start(machine: models.Machine, pod: models.CubePod) -> tuple[int, str]:
    """

    """
    response = subprocess.run(
        f"ssh -t {machine.user}@{machine.ip} 'docker image pull {pod.c_image}'",
        shell=True,
        capture_output=True,
    )

    if response.returncode not in [0]:
        return [response.returncode, response.stdout.decode("utf-8")]

    docker_cmd = pod.docker_run(detach=1)

    response = subprocess.run(
        f"ssh -t {machine.user}@{machine.ip} '{docker_cmd}'",
        shell=True,
        capture_output=True,
    )

    if response.returncode not in [0]:
        return [response.returncode, response.stdout.decode("utf-8")]

    return [response.returncode, ""]


def _machine_docker_stop(machine: models.Machine, pod: models.CubePod) -> tuple[int, str]:
    """
    """
    cmds = [
        f"docker stop {pod.c_name}",
        f"docker rm {pod.c_name}",
    ]

    for cmd in cmds:
        _response = subprocess.run(
            f"ssh -t {machine.user}@{machine.ip} '{cmd}'",
            shell=True,
            capture_output=True,
        )

    return [0, ""]


def _machine_scp(machine: models.Machine, project: models.CubeProject, pod: models.CubePod) -> tuple[int, str]:
    """
    Copy all required files from local machine to host machine, e.g. env files.
    """
    env_path = f"{project.dir}{pod.c_env}"

    if not os.path.exists(env_path):
        return [404, f"env file missing - {env_path}"]

    response = subprocess.run(
        f"scp {env_path} {machine.user}@{machine.ip}:",
        shell=True,
        capture_output=True,
    )

    if response.returncode not in [0]:
        return [response.returncode, response.stdout.decode("utf-8")]

    return [response.returncode, ""]



