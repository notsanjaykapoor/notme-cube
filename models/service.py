SERVICE_DOCKER = "docker"
SERVICE_WORKQ = "workq"
SERVICE_WORKQ_DAEMON = "workq-daemon"
SERVICE_WORKQ_WORKER = "workq-worker"


SERVICES = {
    SERVICE_WORKQ_DAEMON : {
        "docker_entrypoint": "./bin/entrypoint-workq-daemon",
        "docker_image": "us-docker.pkg.dev/notme-330419/notme/notme-cube:latest",
        "docker_run": "docker run --rm -d --name workq-daemon --env-file /usr/apps/workq/env",
        "scp_files": [[".env.workq", "/usr/apps/workq/env"]],
        "ssh_cmds": ["mkdir -p /usr/apps/workq"],
    },
    SERVICE_WORKQ_WORKER : {
        "docker_entrypoint": "./bin/entrypoint-workq-worker",
        "docker_image": "us-docker.pkg.dev/notme-330419/notme/notme-cube:latest",
        "docker_run": "docker run --rm -d --name workq-worker --env-file /usr/apps/workq/env",
        "scp_files": [[".env.workq", "/usr/apps/workq/env"]],
        "ssh_cmds": ["mkdir -p /usr/apps/workq"],
    }
}


def get(service: str) -> dict:
    return SERVICES.get(service) or {}