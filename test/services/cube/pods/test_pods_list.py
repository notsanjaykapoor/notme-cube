import services.cube.pods
import services.cube.projects
import services.files


def test_pods_list():
    projects_list = services.cube.projects.list(path=services.cube.config_path())

    assert projects_list.code == 0
    assert len(projects_list.projects) == 1

    pods_list = services.cube.pods.list(projects=projects_list.projects)

    assert pods_list.code == 0
    assert len(pods_list.pods) == 1

    pod = pods_list.pods[0]

    assert pod.c_env == ".env.cube"
    assert pod.c_image == "docker.io/notsanjay/notme-cube:latest"
    assert pod.c_name == "notme-cube-prd"
    assert pod.c_ports == [9003]
    assert pod.project_name == "notme-cube"

