import services.cube.projects
import services.files


def test_projects_list():
    # should list all projects
    list_result = services.cube.projects.list(path=services.cube.config_path())

    assert list_result.code == 0
    assert len(list_result.projects) == 1

    project = list_result.projects[0]

    assert project.dir == "/Users/sanjaykapoor/notme/notme-cube/deploy/"
    assert project.name == "notme-cube"

    # should list all projects with matching query
    list_result = services.cube.projects.list(path=services.cube.config_path(), query="cube")

    assert list_result.code == 0
    assert len(list_result.projects) == 1

    # should list 0 projects with nomatch query
    list_result = services.cube.projects.list(path=services.cube.config_path(), query="xxx")

    assert list_result.code == 0
    assert len(list_result.projects) == 0
