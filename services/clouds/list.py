import os


def list() -> list[str]:
    """
    list of supported vps providers
    """
    clouds = [s.strip() for s in (os.environ.get("VPS_PROVIDERS") or "").split(",") if s]

    return clouds