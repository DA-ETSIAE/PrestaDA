import os

from utils.casts import cast_to_bool


def get_env_bool(name: str) -> bool:
    env = os.getenv(name, 'False')
    return cast_to_bool(env)
