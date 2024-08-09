import dataclasses
import glob
import os
import re

import services.passw


@dataclasses.dataclass
class Struct:
    code: int
    orgs: list[str]
    errors: list[str]


def orgs_list() -> Struct:
    """
    list password store orgs
    """
    struct = Struct(
        code=0,
        orgs=[],
        errors=[],
    )

    dir_uri= os.environ.get("PASS_DIR_URI")
    _source_host, source_dir, _ = services.passw.file_uri_parse(source_uri=dir_uri)

    files = glob.glob(f"{source_dir}**", recursive=False)

    for file in files:
        match = re.match(rf"({source_dir})(.+)", file)
        org = match[2] # e.g. notme
        struct.orgs.append(org)

    return struct