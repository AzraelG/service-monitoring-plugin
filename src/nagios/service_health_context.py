"""
Nagios Plugin Integration for Service Health Monitoring.

This module defines custom Nagios plugin contexts for evaluating and reporting
the health of a service. It maps service states to Nagios status codes, and
provides custom messages based on the state of the service.

The module utilizes the `nagiosplugin` library to interface with Nagios and report
the status of services.

State Mapping:
    - 0: Ok - Service is up and functioning correctly.
    - 1: Warning - Potential issue detected, further investigation is required.
    - 2: Critical - Service is in a critical state and requires immediate action.
    - 3: Unknown - Service state is unknown; check configuration or logs.

Example Usage:
    service_health = ServiceHealthContext()
    service_health.evaluate(metric, resource)
    service_health.describe(metric)
    service_health.performance(metric, resource)

Modules:
    nagiosplugin
"""

import nagiosplugin

state_mapping = {
    0: nagiosplugin.Ok,
    1: nagiosplugin.Warn,
    2: nagiosplugin.Critical,
    3: nagiosplugin.Unknown
}

state_messages = {
    0: "Service is up.",
    1: "Potential issue detected, investigate soon.",
    2: "Service is in a critical state. Action needed immediately!",
    3: "Service state is unknown, please check the configuration or logs."
}


class ServiceHealthContext(nagiosplugin.Context):
    """
    Custom Nagios plugin context for evaluating and describing the health of a service.

    This class extends `nagiosplugin.Context` and provides methods to map
    the service health status to Nagios states, describe the status with custom messages, 
    and report performance data in Nagios format.

    Attributes:
        name (str): The name of the context, defaulting to 'service_health'.
        custom_description (str): Optional custom message to describe the service health.
    """

    def __init__(self, name="service_health", custom_description=None):
        """
        Initializes the ServiceHealthContext with a name and an optional custom description.

        Args:
            name (str): The name of the context, default is 'service_health'.
            custom_description (str, optional): A custom description to override default messages.
        """
        super().__init__(name)
        self.custom_description = custom_description

    def evaluate(self, metric, resource):
        """
        Evaluates the state of the service and returns the corresponding Nagios state.

        Args:
            metric: The metric that represents the health status of the service.
            resource: The resource being monitored (e.g., a specific service).

        Returns:
            nagiosplugin.Ok, nagiosplugin.Warn, nagiosplugin.Critical, or nagiosplugin.Unknown:
                The Nagios state representing the health of the service.
        """
        return state_mapping.get(metric.value, nagiosplugin.Unknown)

    def describe(self, metric):
        """
        Returns a description of the service health state.

        This method either returns a custom description (if set) or a default message 
        based on the Nagios state of the service.

        Args:
            metric: The metric that represents the health status of the service.

        Returns:
            str: A message describing the service's health state.
        """
        if self.custom_description is not None:
            return self.custom_description
        return state_messages.get(metric.value, "No status available")

    def performance(self, metric, resource):
        """
        Returns performance data for Nagios in the appropriate format.

        This method returns a string in the Nagios performance format that represents
        the health status of the service.

        Args:
            metric: The metric that represents the health status of the service.
            resource: The resource being monitored.

        Returns:
            str: The performance data string in the format "service_status=<value>".
        """
        return f"service_status={metric.value}"
