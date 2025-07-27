"""App"""

import os

from dotenv import load_dotenv

from temply_app.apps import get_app as get_app_root

env_file = os.getenv("env_file")

if env_file:
    load_dotenv(f"{env_file}")


def get_app():
    """Get the app"""
    return get_app_root()


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(get_app(), host="0.0.0.0", port=8000)
