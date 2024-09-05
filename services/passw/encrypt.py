import os

import services.passw


def encrypt(name: str, password: str, user: str="") -> str:
    """
    """
    gpg = services.passw.gpg_get(gpg_dir=os.environ.get("GPG_HOME_URI"))


