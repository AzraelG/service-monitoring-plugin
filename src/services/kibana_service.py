"""
Kibana Service for checking health status.

This module defines the `KibanaService` class, which is a subclass of 
`BaseService`. It provides functionality to check the health status of a 
Kibana service by making a GET request to the `/api/status` endpoint.

The class uses the `HealthStatus` enum to represent the status of the service 
and includes error handling for invalid or misformatted status responses.

Modules:
    enum
    src.services.base_service.BaseService
    src.lib.exceptions.HttpDriverException
    src.lib.exceptions.InvalidHealthStatusError
    src.lib.exceptions.StatusFormatError

Example Usage:
    service = KibanaService(base_endpoint, user, password)
    status = service.get_status()
    print(f"Kibana status: {status}")
"""

from enum import Enum
from src.services.base_service import BaseService
from src.lib.exceptions import InvalidHealthStatusError
from src.lib.exceptions import StatusFormatError

STATUS_CHECK_ENDPOINT = "/api/status"


class HealthStatus(Enum):
    """
    Enum representing the possible health statuses of the Kibana service.

    The possible health statuses are:
        AVAILABLE: Service is operating normally (OK).
        DEGRADED: Service is in a degraded state (Warning).
        CRITICAL: Service is in a critical state (Critical).
        UNAVAILABLE: Service is unavailable (Unknown).

    This enum is used to map the service status returned from the API response.
    """
    AVAILABLE = "OK"
    DEGRADED = "WARNING"
    CRITICAL = "CRITICAL"
    UNAVAILABLE = "UNKNOWN"


class KibanaService(BaseService):
    """
    Service class for interacting with the Kibana health check endpoint.

    The `KibanaService` class is a subclass of `BaseService` that implements 
    the `get_status` method to query the health status of the Kibana service.
    It makes a request to the `/api/status` endpoint and processes the response 
    to return the appropriate health status.

    Attributes:
        base_endpoint (str): The base URL for the Kibana service.
        user (str): The username for authentication.
        password (str): The password for authentication.
        driver (HttpDriver): The HTTP driver to send requests to the service.
        log (logging.Logger): Logger instance for debugging and error logging.
    """

    def get_status(self):
        """
        Retrieves the health status of the Kibana service.

        This method makes a GET request to the `/api/status` endpoint of Kibana 
        and processes the response to determine the service's health status. The 
        status is mapped to one of the values from the `HealthStatus` enum.

        The method performs error handling to catch issues like invalid or misformatted 
        status values in the response, raising custom exceptions in such cases.

        Returns:
            str: The health status of the Kibana service (e.g., "OK", "WARNING", "CRITICAL").

        Raises:
            InvalidHealthStatusError: If the health status received is invalid or not recognized.
            StatusFormatError: If the status format is not a string or is missing.
        """
        try:
            endpoint = f"{self.base_endpoint}{STATUS_CHECK_ENDPOINT}"
            self.log.debug("URL: %s", endpoint)

            response = self.driver.request("GET", endpoint, auth=(
                self.user, self.password), verify=False)
            data = response.json()
            health_status = data["status"]["overall"]["level"].upper()
            status = HealthStatus[health_status]
            return status.value

        except KeyError as e:
            self.log.error("Invalid health status received: %s",
                           data.get("status", {}))
            raise InvalidHealthStatusError(
                f"Invalid health status received: {e}") from e

        except AttributeError as e:
            self.log.error("Status is None or not a string: %s",
                           data.get("status", {}))
            raise StatusFormatError(
                f"Status is None or not a string: {data.get('status', {})}") from e
