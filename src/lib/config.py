import os
from dotenv import load_dotenv

load_dotenv()


class Config():
    """
    Configuration settings loaded from environment variables.
    """
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "5"))
