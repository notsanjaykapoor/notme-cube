import re

import gnupg


def file_uri_parse(source_uri: str) -> tuple[str, str, str]:
    """
    parse file uri into its components:

    'file://localhost//users/dir/file is parsed as:
      - 'localhost' as source_host
      - '/users/dir as source_dir
      - 'file' as source_path
    """
    if not (match := re.match(r'^file:\/\/([^\/]+)\/(.+)$', source_uri)):
        raise ValueError(f"invalid source_uri {source_uri}")

    source_host, source_file_dir = (match[1], match[2])

    if source_file_dir.endswith("/"):
        source_dir = source_file_dir
        source_file = ""
    else:
        match = re.match(r'^(.+)\/(.+)$$', source_file_dir)
        source_dir = match[1]
        source_file = match[2] 

    return source_host, source_dir, source_file


def gpg_get(gpg_dir: str) -> gnupg.GPG:
    """
    get gpg object
    """
    _, source_dir, _ = file_uri_parse(source_uri=gpg_dir)

    return gnupg.GPG(gnupghome=source_dir)


def gpg_key(gpg_dir: str) -> tuple[gnupg.GPG, dict]:
    """
    get gpg key
    """
    gpg = gpg_get(gpg_dir=gpg_dir)

    return (gpg, gpg.list_keys()[0])
