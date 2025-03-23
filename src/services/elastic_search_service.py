from enum import Enum
from src.services.base_service import BaseService
from src.lib.exceptions import HttpDriverException

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
            response = self.driver.request("GET", endpoint, auth=(
                self.user, self.password), verify=False)
            data = response.json()
            health_status = data["status"].upper()
            status = HealthStatus[health_status]
            return status

        except KeyError:
            self.log.error("Invalid health status received: %s", health_status)
            return

        except AttributeError:
            self.log.error("Status is None or not a string: %s",
                           data.get("status"))

        except HttpDriverException as e:
            self.log.error("Error trying to get status: %s", e)

        return HealthStatus.UNKNOWN
