import pytest
import nagiosplugin
from src.lib.exceptions import InvalidNagiosStateError
from src.nagios.service_health_resource import (ServiceHealthResource,
                                                NagiosState)


@pytest.mark.parametrize(
    "service_status, expected_nagios_state, expected_code",
    [
        ("OK", NagiosState.OK, nagiosplugin.Ok.code),
        ("WARNING", NagiosState.WARNING, nagiosplugin.Warn.code),
        ("CRITICAL", NagiosState.CRITICAL, nagiosplugin.Critical.code),
        ("UNKNOWN", NagiosState.UNKNOWN, nagiosplugin.Unknown.code)
    ]
)
def test_probe_valid_status(service_status, expected_nagios_state, expected_code):
    resource = ServiceHealthResource(service_status)
    result = resource.probe()
    assert isinstance(result[0], nagiosplugin.Metric)
    assert result[0].value == expected_code
    assert result[0].name == "service_status"
    assert result[0].context == "service_health"
    assert expected_nagios_state.name == NagiosState(result[0].value).name


def test_probe_invalid_status():
    resource = ServiceHealthResource("INVALID_STATUS")

    with pytest.raises(InvalidNagiosStateError):
        resource.probe()
