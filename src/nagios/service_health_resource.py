import logging
import src.lib.logging_config
import nagiosplugin
from enum import Enum
from src.lib.exceptions import InvalidNagiosStateError


class NagiosState(Enum):
    OK = nagiosplugin.Ok
    WARNING = nagiosplugin.Warn
    CRITICAL = nagiosplugin.Critical
    UNKNOWN = nagiosplugin.Unknown


class ServiceHealthResource(nagiosplugin.Resource):

    def __init__(self, service_status):
        super().__init__()  # Llamada al constructor de la clase base
        self.service_status = service_status
        self.log = logging.getLogger(__name__)
        self.log.debug(
            "Initializing ServiceHealthResource with status: %s", service_status)

    def probe(self):
        """
        Convert status string to Enum values, raising an error for invalid inputs
        """
        try:
            self.log.info("Probing service status: %s", self.service_status)
            nagios_state = NagiosState[self.service_status.upper()]
            self.log.debug("Mapped service status %s to Nagios state %s",
                           self.service_status, nagios_state.name)
        except KeyError as e:
            self.log.error("Invalid service status received: %s",
                           self.service_status)
            raise InvalidNagiosStateError(self.service_status) from e

        self.log.info("Returning metric for service status: %s",
                      nagios_state.name)
        return [nagiosplugin.Metric("service_status", nagios_state.value.code, context="service_health")]
