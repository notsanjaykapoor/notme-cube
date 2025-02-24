import os

import nats
import nats.aio.client


async def connect(name: str) -> nats.aio.client.Client:
    """
    Connect to nats server, returns a nat client object.
    """
    nats_uri = os.environ.get("NATS_URI")

    nats_options = {
        "name": name,
    }

    if nats_creds := os.environ.get("NATS_CREDS"):
        nats_options["user_credentials"] = nats_creds

    nats_client = await nats.connect(nats_uri, **nats_options)

    return nats_client

