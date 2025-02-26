import os

import services.clouds


def default() -> str:
    return services.clouds.list()[0]