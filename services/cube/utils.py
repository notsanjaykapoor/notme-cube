import os

import services.files


def config_path() -> str:
    source_path, _, _ = services.files.file_uri_parse(source_uri=os.environ.get("CUBE_CONFIG_PATH"))

    return source_path
