import pytest
from unittest.mock import MagicMock
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
    metric = MagicMock()
    metric.value = metric_value

    context = ServiceHealthContext("service_health")

    state = context.evaluate(metric, None)

    assert state == expected_state

    description = context.describe(metric)
    assert description == expected_message


def test_custom_description():
    metric = MagicMock()
    metric.value = 0
    context = ServiceHealthContext(
        "service_health", custom_description="Custom OK Message")
    description = context.describe(metric)
    assert description == "Custom OK Message"


def test_performance():
    metric = MagicMock()
    metric.value = 0

    context = ServiceHealthContext("service_health")

    performance_data = context.performance(metric, None)
    assert performance_data == "service_status=0"
