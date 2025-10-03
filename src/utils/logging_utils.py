import logging
import os

log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "admin_changes.log"))

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def log_admin_env_change(username, env_dict):
    logging.info(f"{username} updated .env to: {env_dict}")
