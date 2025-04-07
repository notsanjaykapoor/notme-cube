import models
import services.clusters
import services.hetzner.servers
import services.hetzner.ssh_keys
import services.machines
import services.machines.containers
import services.ssh

def machine_add(cluster: models.Cluster, machine_name: str="", machine_tags: dict={}) -> tuple[int, models.Machine]:
    """
    Add machine to cluster.
    """
    list_result = services.machines.list(cluster=cluster)
    machines_list = list_result.objects_list

    if list_result.objects_map.get(machine_name):
        # machine exists
        return 409, None

    # generate new machine name
    if not machine_name:
        machine_name = services.clusters.machine_name_generate(
            cluster=cluster,
            names=[machine.name for machine in machines_list],
        )

    # get primary ssh key
    ssh_keys_struct = services.hetzner.ssh_keys.list()
    ssh_key_name = ssh_keys_struct.objects[0].name

    # generate machine tags
    machine_tags_merged = machine_tags | {
        "cluster": cluster.name,
    }

    # add machine to cluster
    create_result = services.hetzner.servers.create(
        cluster=cluster,
        name=machine_name,
        ssh_key=ssh_key_name,
        tags=machine_tags_merged,
    )

    code = create_result.code
    machine = create_result.machine

    if code == 0:
        # verify machine ssh connection
        code, _result = services.ssh.verify(host=machine.ip, user=machine.user, retries=5)

    return code, machine


def machine_remove(cluster: models.Cluster, machine_name: str) -> int:
    """
    Remove machine from cluster.
    """
    list_result = services.machines.list(cluster=cluster)

    if machine_name:
        # get specific machine
        machines_map = list_result.objects_map
        machine = machines_map.get(machine_name)
    else:
        # get any machine
        machine = list_result.objects_list[0]

    if not machine:
        return -1

    # stop machine containers

    _stop_result = services.machines.containers.stop(machine=machine)

    # delete server

    services.hetzner.servers.delete(id=machine.id)

    return 0
