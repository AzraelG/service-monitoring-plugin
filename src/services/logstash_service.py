"""
Logstash Service for checking health status based on CPU usage.

This module defines the `LogstashService` class, which is a subclass of 
`BaseService`. It provides functionality to check the health status of a 
Logstash service by making a GET request to the `/_node/stats/process` endpoint.

The health status is determined based on the CPU usage of the Logstash process:
- `OK` if the CPU usage is below 70%.
- `WARNING` if the CPU usage is between 70% and 85%.
- `CRITICAL` if the CPU usage exceeds 85%.
- `UNKNOWN` if there is an error or invalid CPU usage data.

Modules:
    enum
    src.services.base_service.BaseService
    src.lib.exceptions.InvalidHealthStatusError

Example Usage:
    service = LogstashService(base_endpoint, user, password)
    status = service.get_status()
    print(f"Logstash status: {status}")
"""

from enum import Enum
from src.services.base_service import BaseService
from src.lib.exceptions import InvalidHealthStatusError

STATUS_CHECK_ENDPOINT = "/_node/stats/process"


class HealthStatus(Enum):
    """
    Enum representing the possible health statuses of the Logstash service.

    The possible health statuses are:
        OK: CPU usage is below 70%.
        WARNING: CPU usage is between 70% and 85%.
        CRITICAL: CPU usage is above 85%.
        UNKNOWN: Error or invalid CPU usage value.

    This enum is used to map the CPU usage values to a health status.
    """
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class LogstashService(BaseService):
    """
    Service class for interacting with the Logstash health check endpoint.

    The `LogstashService` class is a subclass of `BaseService` that implements 
    the `get_status` method to query the health status of the Logstash service.
    It makes a request to the `/_node/stats/process` endpoint and processes 
    the CPU usage data to determine the service's health status.

    Attributes:
        base_endpoint (str): The base URL for the Logstash service.
        user (str): The username for authentication.
        password (str): The password for authentication.
        driver (HttpDriver): The HTTP driver to send requests to the service.
        log (logging.Logger): Logger instance for debugging and error logging.
    """

    def get_status(self):
        """
        Retrieves the health status of the Logstash service based on CPU usage.

        This method makes a GET request to the `/_node/stats/process` endpoint of 
        Logstash, processes the CPU usage value, and returns the corresponding 
        health status based on predefined thresholds:
            - OK: CPU usage below 70%.
            - WARNING: CPU usage between 70% and 85%.
            - CRITICAL: CPU usage above 85%.
            - UNKNOWN: If there is an error or invalid CPU usage data.

        The method includes error handling for missing keys, invalid data, and 
        other issues related to the CPU usage value.

        Returns:
            str: The health status of the Logstash service (e.g., "OK", "WARNING", "CRITICAL").

        Raises:
            InvalidHealthStatusError: If there is an issue processing the health status data, 
                                       such as missing keys or invalid values.
        """

        try:
            endpoint = f"{self.base_endpoint}{STATUS_CHECK_ENDPOINT}"
            self.log.debug("URL: %s", endpoint)
            response = self.driver.request("GET", endpoint, auth=(
                self.user, self.password), verify=False)
            data = response.json()
            cpu_usage = int(data["process"]["cpu"]["percent"])
            if (cpu_usage < 70):
                health_status = HealthStatus.OK
            elif (70 <= cpu_usage < 85):
                health_status = HealthStatus.WARNING
            elif (cpu_usage >= 85):
                health_status = HealthStatus.CRITICAL
            else:
                self.log.warning("Invalid CPU usage value: %s", cpu_usage)
                health_status = HealthStatus.UNKNOWN
            return health_status.value

        except KeyError as e:
            self.log.error("Error processing health data, missing key: %s", e)
            raise InvalidHealthStatusError(
                f"Invalid health status data, missing key: {e}") from e

        except ValueError as e:
            self.log.error("Invalid CPU usage value: %s",
                           data["process"]["cpu"].get("percent"))
            raise InvalidHealthStatusError(
                f"Invalid CPU usage value: {e}") from e

        except TypeError as e:
            self.log.error("Invalid CPU usage value: %s",
                           data["process"]["cpu"].get("percent"))
            raise InvalidHealthStatusError(
                f"Invalid CPU usage value: {e}") from e
