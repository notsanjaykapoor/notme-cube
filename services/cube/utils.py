import os

import services.files


def config_path() -> str:
    _, source_dir, source_file = services.files.file_uri_parse(source_uri=os.environ.get("CUBE_CONFIG_PATH"))

    return f"{source_dir}{source_file}"
