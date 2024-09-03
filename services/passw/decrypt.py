import os
import re

import models
import services.passw


def decrypt(passw: models.Passw) -> models.Passw:
    """
    decrypt password object using gpg key
    """
    gpg = services.passw.gpg_get(gpg_dir=os.environ.get("GPG_HOME_URI"))

    decrypted_data = gpg.decrypt_file(open(passw.path, "rb"))
    plaintext = str(decrypted_data)

    secret, *other = plaintext.split("\n")
    other = [s for s in other if s]

    passw.passw = secret

    if other and re.search(r"^(email:|id.*:|user.*:)", other[0]):
        passw.user = other[0].split(":")[1].strip()

    return passw

