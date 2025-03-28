"""
Configuration settings for the application.

This module loads configuration settings from environment variables using the 
`python-dotenv` package. It provides a central location for managing settings 
such as timeouts, credentials, and other environment-specific configurations 
required by the application.

Example:
    HTTP_TIMEOUT: Defines the timeout (in seconds) for HTTP requests. The 
    default value is 5 seconds if not set in the environment.

Usage:
    To access configuration values:
        config = Config()
        print(config.HTTP_TIMEOUT)
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config():
    """
    Configuration settings loaded from environment variables.
    """
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "5"))
