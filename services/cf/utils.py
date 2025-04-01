import os


def account_id() -> str:
    """
    Return cloudflare account id
    """
    return os.environ.get("CLOUDFLARE_ACCOUNT_ID")