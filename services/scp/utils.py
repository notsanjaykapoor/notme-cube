import subprocess


def exec(host: str, user: str, src: str, dst: str) -> tuple[int, list]:
    response = subprocess.run(
        f"scp {src} {user}@{host}:{dst}",
        shell=True,
        capture_output=True,
    )

    code = response.returncode

    if code == 0:
        result = response.stdout.decode("utf-8")
    else:
        result = response.stderr.decode("utf-8")
         
    return code, result

