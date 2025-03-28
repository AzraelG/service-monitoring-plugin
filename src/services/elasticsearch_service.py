"""
Elasticsearch Service for checking health status.

This module defines the `ElasticsearchService` class, which is a subclass of 
`BaseService`. It provides functionality to check the health status of an 
Elasticsearch service by making a GET request to the health check endpoint.

The class uses the `HealthStatus` enum to represent the status of the service 
and provides error handling for invalid or misformatted status responses.

Modules:
    enum
    src.services.base_service.BaseService
    src.lib.exceptions.InvalidHealthStatusError
    src.lib.exceptions.StatusFormatError

Example Usage:
    service = ElasticsearchService(base_endpoint, user, password)
    status = service.get_status()
    print(f"Elasticsearch status: {status}")
"""

from enum import Enum
from src.services.base_service import BaseService
from src.lib.exceptions import InvalidHealthStatusError
from src.lib.exceptions import StatusFormatError

STATUS_CHECK_ENDPOINT = "/_health_report"


class HealthStatus(Enum):
    """
    Enum representing the possible health statuses of the service.

    The possible health statuses are:
        GREEN: Service is operating normally (OK).
        YELLOW: Service is in a warning state (Warning).
        RED: Service is in a critical state (Critical).
        UNKNOWN: Service health status is unknown.

    This enum is used to map the service status returned from the API response.
    """

    GREEN = "OK"
    YELLOW = "WARNING"
    RED = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ElasticsearchService(BaseService):
    """
    Service class for interacting with Elasticsearch health check endpoint.

    The `ElasticsearchService` class is a subclass of `BaseService` that implements 
    the `get_status` method to query the health status of the Elasticsearch service.
    It makes a request to the health check endpoint and processes the response to 
    return the appropriate health status.

    Attributes:
        base_endpoint (str): The base URL for the Elasticsearch service.
        user (str): The username for authentication.
        password (str): The password for authentication.
        driver (HttpDriver): The HTTP driver to send requests to the service.
        log (logging.Logger): Logger instance for debugging and error logging.
    """

    def get_status(self):
        """
        Retrieves the health status of the Elasticsearch service.

        This method makes a GET request to the Elasticsearch health check endpoint 
        and processes the response to determine the service's health status. The 
        status is mapped to one of the values from the `HealthStatus` enum.

        The method performs error handling to catch issues like invalid or misformatted 
        status values in the response, raising custom exceptions in such cases.

        Returns:
            str: The health status of the Elasticsearch service (e.g., "OK", "WARNING", "CRITICAL").

        Raises:
            InvalidHealthStatusError: If the health status received is invalid or not recognized.
            StatusFormatError: If the status format is not a string or is missing.
        """
        try:
            endpoint = f"{self.base_endpoint}{STATUS_CHECK_ENDPOINT}"
            self.log.debug("url: %s", self.base_endpoint)
            response = self.driver.request("GET", endpoint, auth=(
                self.user, self.password), verify=False)
            data = response.json()
            health_status = data["status"].upper()
            status = HealthStatus[health_status]
            return status.value

        except KeyError as e:
            self.log.error("Invalid health status received: %s",
                           data.get("status"))
            raise InvalidHealthStatusError(
                f"Invalid health status received: {e}") from e

        except AttributeError as e:
            self.log.error("Status is None or not a string: %s",
                           data.get("status"))
            raise StatusFormatError(
                f"Status is None or not a string: {data.get('status')}") from e
