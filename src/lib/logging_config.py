import logging
import os

default_log_dir = os.path.join(os.path.expanduser("~"), ".logs")
default_log_file = os.path.join(default_log_dir, "app.log")
log_file_path = os.getenv("LOG_PATH", default_log_file)
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()

logging.basicConfig(
    level=getattr(logging, log_level, logging.DEBUG),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path)
    ]
)
