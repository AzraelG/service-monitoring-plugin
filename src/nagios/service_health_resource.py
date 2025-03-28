"""
Nagios Plugin Integration for Service Health Resource.

This module defines a `ServiceHealthResource` class that is used to probe the
status of a service and map it to corresponding Nagios states (OK, WARNING, 
CRITICAL, UNKNOWN). The module also defines an enumeration `NagiosState` that 
maps service health states to Nagios plugin states.

The `ServiceHealthResource` class provides a way to convert a service status 
string to a corresponding Nagios state and return a metric for the Nagios plugin.

Modules:
    logging
    src.lib.logging_config
    nagiosplugin
    enum
    src.lib.exceptions

Exceptions:
    InvalidNagiosStateError: Raised when an invalid service status is provided.

Example Usage:
    resource = ServiceHealthResource("OK")
    metrics = resource.probe()
    for metric in metrics:
        print(metric)
"""

import logging
import src.lib.logging_config
import nagiosplugin
from enum import Enum
from src.lib.exceptions import InvalidNagiosStateError


class NagiosState(Enum):
    """
    Enum representing the different Nagios states for service health.

    The values of this enum correspond to the respective Nagios plugin states:
    - nagiosplugin.Ok
    - nagiosplugin.Warn
    - nagiosplugin.Critical
    - nagiosplugin.Unknown
    """

    OK = nagiosplugin.Ok
    WARNING = nagiosplugin.Warn
    CRITICAL = nagiosplugin.Critical
    UNKNOWN = nagiosplugin.Unknown


class ServiceHealthResource(nagiosplugin.Resource):
    """
    A resource for Nagios plugin that monitors and probes the health status 
    of a service.

    This class is used to probe a service's status and convert it to a corresponding 
    Nagios state (OK, WARNING, CRITICAL, UNKNOWN). It also returns a Nagios metric 
    for reporting the service status.

    Attributes:
        context (str): The context for the Nagios plugin, defaults to 'service_health'.
        service_status (str): The status of the service (e.g., 'OK', 'WARNING').
        log (logging.Logger): Logger instance for debugging and error logging.
    """

    def __init__(self, service_status, context="service_health"):
        """
        Initializes the `ServiceHealthResource` with the given service status and context.

        Args:
            service_status (str): The status of the service (e.g., 'OK', 'WARNING').
            context (str): The context for the Nagios plugin, defaults to 'service_health'.
        """
        super().__init__()
        self.context = context
        self.service_status = service_status
        self.log = logging.getLogger(__name__)
        self.log.debug(
            "Initializing ServiceHealthResource with status: %s", service_status)

    def probe(self):
        """
        Probes the service status, converts it to a corresponding Nagios state, and 
        returns the Nagios metric.

        This method converts the `service_status` string to a corresponding Nagios state
        (OK, WARNING, CRITICAL, UNKNOWN). If the status is invalid, it raises 
        an `InvalidNagiosStateError`.

        Returns:
            list: A list containing a Nagios metric with the service status.

        Raises:
            InvalidNagiosStateError: If the provided service status is invalid or not recognized.
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
        return [nagiosplugin.Metric("service_status", nagios_state.value.code, context=self.context)]
