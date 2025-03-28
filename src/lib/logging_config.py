"""
Logging configuration for the application.

This module sets up logging for the application, allowing logs to be written to
a file in the `.log/` directory at the root of the project. The log file is named
`app.log`, and the log level can be configured through the environment variable 
`LOG_LEVEL` (defaulting to `INFO` if not set). The log file location can be 
customized using the `LOG_PATH` environment variable.

The logging setup includes:
- A file handler that writes log messages to the log file.
- A default log format that includes the timestamp, logger name, log level, and message.
- A mechanism to create the `.log/` directory if it doesn't exist.

Example usage:
    1. Set the environment variable `LOG_LEVEL` to configure the log level (e.g., DEBUG, INFO).
    2. Optionally, set the `LOG_PATH` to specify a custom log file path.

Log file location:
    By default, the log file is stored at:
    <project_root>/.log/app.log

Modules:
    logging
    os
"""

import logging
import os

project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", ".."))
default_log_dir = os.path.join(project_root, ".log")
default_log_file = os.path.join(default_log_dir, "app.log")
log_file_path = os.getenv("LOG_PATH", default_log_file)
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path)
    ]
)
