"""
HttpDriver module for sending HTTP requests with configurable timeout.

This module defines the `HttpDriver` class, which provides a simple
interface for making HTTP requests while handling connection errors
gracefully.

Classes:
    HttpDriver: A simple HTTP driver for making requests with a configurable timeout.

Exceptions:
    HttpDriverException: Raised when an HTTP connection error occurs.
"""

import logging
import requests
from src.lib.config import Config
from src.lib.exceptions import HttpDriverException
from src.lib.exceptions import HttpConnectionError
from src.lib.exceptions import HttpTimeoutError
from src.lib.exceptions import HttpStatusError
from src.lib.exceptions import HttpUnexpectedError


class HttpDriver():
    """
    A simple HTTP driver for making requests with a configurable timeout.

    Attributes:
        timeout (int): The timeout for requests, loaded from the configuration.
        log (logging.Logger): Logger instance for debugging and error logging.
    """

    def __init__(self) -> None:
        self.timeout = Config.HTTP_TIMEOUT
        self.log = logging.getLogger(__name__)

    def request(self, method, url, **kwargs) -> requests.Response:
        """
        Sends an HTTP request using the given method and URL.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            url (str): The target URL for the request.
            **kwargs: Additional arguments passed to `requests.request`, such as headers or data.

        Returns:
            requests.Response: The HTTP response object.

        Raises:
            HttpDriverException: If a connection error occurs.
        """

        kwargs.setdefault('timeout', self.timeout)
        data = kwargs.get('data', None)
        self.log.debug("Sending request: %s %s", method, url)
        self.log.debug("Body: %s", data)
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()

        except requests.exceptions.ConnectionError as e:
            self.log.error(e)
            raise HttpConnectionError(
                "Error trying to connect to HTTP server") from e

        except requests.exceptions.Timeout as e:
            self.log.error("Request timeout: %s", str(e))
            raise HttpTimeoutError("Request timed out") from e

        except requests.exceptions.HTTPError as e:
            if e.response is not None:  # Ensure response exists before accessing
                self.log.error("HTTP error (%d): %s",
                               e.response.status_code, e.response.text)
                if e.response.status_code == 401:
                    raise HttpStatusError("Authentication failed") from e
                raise HttpStatusError(
                    f"HTTP error occurred: {e.response.status_code}") from e
            else:
                self.log.error("HTTP error occurred with no response details.")
                raise HttpDriverException("HTTP error occurred") from e

        except requests.exceptions.RequestException as e:
            self.log.error("Unexpected request error: %s", str(e))
            raise HttpUnexpectedError(f"Unexpected error: {str(e)}") from e

        self.log.debug("Response: %s", response.text)
        return response
