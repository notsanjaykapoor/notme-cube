import os
import re

import gnupg

import models
import services.passw


def decrypt(passw: models.Passw) -> models.Passw:
    dir_uri= os.environ.get("GPG_HOME_URI")
    _, source_dir, _ = services.passw.file_uri_parse(source_uri=dir_uri)

    gpg = gnupg.GPG(gnupghome=source_dir)
    decrypted_data = gpg.decrypt_file(open(passw.path, "rb"))
    plaintext = str(decrypted_data)

    secret, *other = plaintext.split("\n")
    other = [s for s in other if s]

    passw.passw = secret

    if other and re.search(r"^(email:|user:)", other[0]):
        passw.user = other[0].split(":")[1].strip()

    return passw

