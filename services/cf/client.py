import os

import cloudflare


def client():
    """
    Initialize and return a cloudflare client
    """
    client = cloudflare.Cloudflare(
        api_email=os.environ.get("CLOUDFLARE_EMAIL"),
        api_key=os.environ.get("CLOUDFLARE_API_KEY"),
    )

    return client