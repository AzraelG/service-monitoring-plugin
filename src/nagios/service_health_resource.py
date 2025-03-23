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

    def probe(self):
        """Convert status string to Enum values, raising an error for invalid inputs"""
        try:
            nagios_state = NagiosState[self.service_status.upper()]
        except KeyError as e:
            raise InvalidNagiosStateError(
                self.service_status) from e

        return [nagiosplugin.Metric('service_status', nagios_state.value.code, context='service_health')]
