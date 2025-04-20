SERVICE_DOCKER = "docker"
SERVICE_WORKQ = "workq"
SERVICE_WORKQ_ROUTER = "workq-router"
SERVICE_WORKQ_WORKER = "workq-worker"


SERVICES = {
    SERVICE_WORKQ_ROUTER : {
        "docker_entrypoint": "./bin/entrypoint-workq-router $cluster",
        "docker_image": "docker.io/notsanjay/notme-cube:latest",
        "docker_run": "docker run --rm -d --name workq-router --env-file /usr/apps/workq/env",
        "scp_files": [[".env.workq", "/usr/apps/workq/env"]],
        "ssh_cmds": ["mkdir -p /usr/apps/workq"],
    },
    SERVICE_WORKQ_WORKER : {
        "docker_entrypoint": "./bin/entrypoint-workq-worker $cluster",
        "docker_image": "docker.io/notsanjay/notme-cube:latest",
        "docker_run": "docker run --rm -d --name workq-worker --env-file /usr/apps/workq/env",
        "scp_files": [[".env.workq", "/usr/apps/workq/env"]],
        "ssh_cmds": ["mkdir -p /usr/apps/workq"],
    }
}


def get(service: str) -> dict:
    return SERVICES.get(service) or {}