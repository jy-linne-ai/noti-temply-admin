"""App"""

import os

from dotenv import load_dotenv

from temply_app.apps import create_app
from temply_app.core.config import Config

env_file = os.getenv("env_file")

if env_file:
    load_dotenv(f"{env_file}")

app = create_app(Config())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
