from enum import Enum
from src.services.base_service import BaseService
from src.lib.exceptions import HttpDriverException
from src.lib.exceptions import InvalidHealthStatusError
from src.lib.exceptions import StatusFormatError
from src.lib.exceptions import ServiceRequestError

status_check_endpoint = "/_cluster/health"


class HealthStatus(Enum):
    GREEN = "OK"
    YELLOW = "WARNING"
    RED = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ElasticSearchService(BaseService):

    def get_status(self):
        try:
            endpoint = f"{self.base_endpoint}{status_check_endpoint}"
            self.log.debug("url: %s", self.base_endpoint)
            response = self.driver.request("GET", endpoint, auth=(
                self.user, self.password), verify=False)
            data = response.json()
            health_status = data["status"].upper()
            status = HealthStatus[health_status]
            return status.value

        except KeyError as e:
            self.log.error("Invalid health status received: %s", health_status)
            raise InvalidHealthStatusError(
                f"Invalid health status received: {e}") from e

        except AttributeError as e:
            self.log.error("Status is None or not a string: %s",
                           data.get("status"))
            raise StatusFormatError(
                f"Status is None or not a string: {data.get('status')}") from e

        except HttpDriverException as e:
            self.log.error("Error trying to get status: %s", e)
            raise ServiceRequestError(
                f"Error trying to get status: {e}") from e
