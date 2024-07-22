import os


def clouds() -> list[str]:
    """
    list of vps providers supported
    """
    clouds = [s.strip() for s in (os.environ.get("VPS_PROVIDERS") or "").split(",") if s]

    return clouds