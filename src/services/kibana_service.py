from enum import Enum
from src.services.base_service import BaseService
from src.lib.exceptions import HttpDriverException
from src.lib.exceptions import InvalidHealthStatusError
from src.lib.exceptions import StatusFormatError

STATUS_CHECK_ENDPOINT = "/api/status"


class HealthStatus(Enum):
    AVAILABLE = "OK"
    DEGRADED = "WARNING"
    CRITICAL = "CRITICAL"
    UNAVAILABLE = "UNKNOWN"


class KibanaService(BaseService):

    def get_status(self):
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
