import sqlmodel

import services.clusters


def test_cluster_machine_names_alpha(db_session: sqlmodel.Session):
    cluster = services.clusters.create(
        db_session=db_session,
        name="test",
        services="workq",
    )

    machine_name = services.clusters.machine_name_generate(cluster=cluster, names=[])

    assert(machine_name) == "test-1"

    machine_name = services.clusters.machine_name_generate(cluster=cluster, names=["test-0"])

    assert(machine_name) == "test-1"

    machine_name = services.clusters.machine_name_generate(cluster=cluster, names=["test-1", "test-3"])

    assert(machine_name) == "test-4"

    db_session.delete(cluster)
    db_session.commit()


def test_cluster_machine_names_alphanum(db_session: sqlmodel.Session):
    cluster = services.clusters.create(
        db_session=db_session,
        name="test-0",
        services="workq",
    )

    machine_name = services.clusters.machine_name_generate(cluster=cluster, names=[])

    assert(machine_name) == "test-0-1"

    machine_name = services.clusters.machine_name_generate(cluster=cluster, names=["test-0-0"])

    assert(machine_name) == "test-0-1"

    machine_name = services.clusters.machine_name_generate(cluster=cluster, names=["test-0-1", "test-0-3"])

    assert(machine_name) == "test-0-4"

    machine_name = services.clusters.machine_name_generate(cluster=cluster, names=["test-0-1", "test-0-9"])

    assert(machine_name) == "test-0-10"

    db_session.delete(cluster)
    db_session.commit()
