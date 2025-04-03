import models


def machine_name_generate(cluster: models.Cluster, names: list[str]) -> str:
    """
    Generate a unique machine name for the cluster
    """
    name_pre = f"{cluster.name}-"

    ids = [int(name.replace(name_pre, "")) for name in names if name.startswith(name_pre)]

    if not ids:
        return f"{name_pre}1"

    return f"{name_pre}{ids[-1]+1}"
