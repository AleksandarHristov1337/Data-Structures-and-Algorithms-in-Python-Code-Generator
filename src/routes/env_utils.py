import os
from flask_login import current_user
from utils.logging_utils import log_admin_env_change

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),  "..", "..", ".env"))

DEFAULT_ENV_CONTENT = """GOOGLE_API_KEY=
MODEL_NAME=gemini-2.0-flash-001
"""

def read_env():
    if not os.path.exists(ENV_PATH):
        with open(ENV_PATH, "w") as f:
            f.write(DEFAULT_ENV_CONTENT)
    with open(ENV_PATH, "r") as f:
        lines = f.readlines()
    env_dict = {}
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.strip().split("=", 1)
            env_dict[key] = value
    return env_dict

def write_env(env_dict):
    with open(ENV_PATH, "w") as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")
    user = current_user.username if current_user.is_authenticated else "unknown"
    log_admin_env_change(user, env_dict)
