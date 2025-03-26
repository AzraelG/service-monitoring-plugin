from enum import Enum
from src.services.base_service import BaseService
from src.lib.exceptions import HttpDriverException
from src.lib.exceptions import InvalidHealthStatusError
from src.lib.exceptions import ServiceRequestError

STATUS_CHECK_ENDPOINT = "/_node/stats/process"


class HealthStatus(Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class LogstashService(BaseService):

    def get_status(self):
        try:
            endpoint = f"{self.base_endpoint}{STATUS_CHECK_ENDPOINT}"
            self.log.debug("URL: %s", endpoint)
            response = self.driver.request("GET", endpoint, auth=(
                self.user, self.password), verify=False)
            data = response.json()
            cpu_usage = data["process"]["cpu"]["percent"]
            if cpu_usage < 70:
                health_status = HealthStatus.OK
            elif 70 <= cpu_usage < 85:
                health_status = HealthStatus.WARNING
            elif cpu_usage >= 85:
                health_status = HealthStatus.CRITICAL
            else:
                self.log.warning("Invalid CPU usage value: %s", cpu_usage)
                health_status = HealthStatus.UNKNOWN
            return health_status.value

        except KeyError as e:
            self.log.error("Error processing health data, missing key: %s", e)
            raise InvalidHealthStatusError(
                f"Invalid health status data, missing key: {e}") from e
