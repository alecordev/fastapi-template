import os
import pathlib

import version

BASE_DIR = pathlib.Path(__file__).resolve().parent

API_VERSION = os.getenv("API_VERSION", version.__version__)
API_TITLE = os.getenv("API_TITLE", "API Template")
API_PORT = int(os.getenv("API_PORT", "8081"))

API_KEY = os.getenv("API-KEY", "password")
API_KEY_NAME = os.getenv("API-KEY-NAME", "x-api-key")
