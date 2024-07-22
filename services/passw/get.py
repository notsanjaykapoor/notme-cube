import os

import models
import services.passw


def get_by_name(name: str) -> models.Passw | None:
    dir_uri= os.environ.get("PASS_DIR_URI")
    source_host, source_dir, _ = services.passw.file_uri_parse(source_uri=dir_uri)

    file_path = f"{source_dir}{name}"

    if not file_path.endswith("gpg"):
        file_path = f"{file_path}.gpg"

    if not os.path.exists(file_path):
        return None
    
    passw = models.Passw(
        name=name,
        path=file_path,
        uri=f"file://{source_host}/{file_path}"
    )

    return passw