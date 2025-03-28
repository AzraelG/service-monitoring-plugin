"""
Unit tests for the `ServiceHealthContext` class in the `src.nagios.service_health_context` module.

This module tests the functionality of the `ServiceHealthContext` class, which evaluates and describes 
the health of a service based on a given metric value.

Tests:
- `test_evaluate_and_describe`: Verifies that the service health is evaluated correctly and 
  the correct description is generated based on the metric value (e.g., OK, Warn, Critical, Unknown).
- `test_custom_description`: Tests the ability to set a custom description when creating 
  a `ServiceHealthContext`.
- `test_performance`: Verifies the performance data output based on the service health context.

Dependencies:
- `pytest`: A testing framework for Python.
- `nagiosplugin`: A Nagios plugin for monitoring services.
- `ServiceHealthContext`: The service health evaluation and description class under test.
"""

from unittest.mock import MagicMock
import pytest
import nagiosplugin
from src.nagios.service_health_context import ServiceHealthContext


@pytest.mark.parametrize(
    "metric_value, expected_state, expected_message",
    [
        (0, nagiosplugin.Ok, "Service is up."),
        (1, nagiosplugin.Warn, "Potential issue detected, investigate soon."),
        (2, nagiosplugin.Critical,
         "Service is in a critical state. Action needed immediately!"),
        (3, nagiosplugin.Unknown,
         "Service state is unknown, please check the configuration or logs."),
    ]
)
def test_evaluate_and_describe(metric_value, expected_state, expected_message):
    """
    Test evaluating and describing service health based on metric value.

    This test verifies that the `evaluate` method of `ServiceHealthContext` correctly determines the 
    state of the service based on the given metric value, and that the `describe` method provides 
    the corresponding description message.

    Args:
        metric_value (int): The metric value used to evaluate the service health.
        expected_state (NagiosPluginState): The expected state (Ok, Warn, Critical, or Unknown).
        expected_message (str): The expected description message for the service health state.

    Asserts:
        - The state returned by `evaluate` matches the expected state.
        - The description returned by `describe` matches the expected message.
    """

    metric = MagicMock()
    metric.value = metric_value

    context = ServiceHealthContext("service_health")

    state = context.evaluate(metric, None)

    assert state == expected_state

    description = context.describe(metric)
    assert description == expected_message


def test_custom_description():
    """
    Test setting and using a custom description.

    This test verifies that a custom description can be set when creating a `ServiceHealthContext` 
    instance, and that it is used when calling the `describe` method.

    Asserts:
        - The description returned by `describe` matches the custom description set during 
          initialization.
    """

    metric = MagicMock()
    metric.value = 0
    context = ServiceHealthContext(
        "service_health", custom_description="Custom OK Message")
    description = context.describe(metric)
    assert description == "Custom OK Message"


def test_performance():
    """
    Test the performance data output for service health.

    This test ensures that the `performance` method of `ServiceHealthContext` returns the correct 
    performance data string based on the metric value.

    Asserts:
        - The performance data returned by `performance` matches the expected format.
    """

    metric = MagicMock()
    metric.value = 0

    context = ServiceHealthContext("service_health")

    performance_data = context.performance(metric, None)
    assert performance_data == "service_status=0"
