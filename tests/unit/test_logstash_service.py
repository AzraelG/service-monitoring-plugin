import pytest
from unittest.mock import patch, MagicMock
import requests
from src.services.logstash_service import LogstashService
from src.lib.exceptions import HttpDriverException
from src.lib.exceptions import InvalidHealthStatusError


@pytest.mark.parametrize(
    "cpu_usage, expected_health_status",
    [
        (50, "OK"),
        (75, "WARNING"),
        (90, "CRITICAL")
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_get_status_valid(mock_request, cpu_usage, expected_health_status):
    """
    Test valid health statuses based on CPU usage.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "process": {"cpu": {"percent": cpu_usage}}}
    mock_request.return_value = mock_response

    service = LogstashService(
        user="user", password="password", base_endpoint="http://localhost:9600")
    status = service.get_status()
    assert status == expected_health_status

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False, timeout=5
    )


@pytest.mark.parametrize(
    "exception, expected_message",
    [
        (requests.exceptions.ConnectionError,
         "Error trying to connect to HTTP server"),
        (requests.exceptions.Timeout, "Request timed out"),
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_get_status_error_handling(mock_request, exception, expected_message):
    """
    Test handling of connection errors and timeouts.
    """
    mock_request.side_effect = exception

    service = LogstashService(
        user="user", password="password", base_endpoint="http://localhost:9600")

    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False, timeout=5
    )


@pytest.mark.parametrize(
    "status_code, expected_message",
    [
        (401, "Authentication failed"),
        (403, "HTTP error occurred: 403"),
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_get_status_authentication_failure(mock_request, status_code, expected_message):
    """
    Test authentication failures (HTTP 401, 403).
    """
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {"message": "Unauthorized"}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response)
    mock_request.return_value = mock_response

    service = LogstashService(
        user="user", password="password", base_endpoint="http://localhost:9600")

    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False, timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_invalid_response(mock_request):
    """
    Test handling of a response missing the "process" field.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    service = LogstashService(
        user="user", password="password", base_endpoint="http://localhost:9600")

    with pytest.raises(InvalidHealthStatusError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False, timeout=5
    )


@pytest.mark.parametrize(
    "invalid_cpu_value",
    [
        None,
        "not_a_number",
        {},
        [],
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_get_status_invalid_cpu_value(mock_request, invalid_cpu_value):
    """
    Test handling of a response with an invalid CPU value (e.g., not a number).
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "process": {"cpu": {"percent": invalid_cpu_value}}}
    mock_request.return_value = mock_response

    service = LogstashService(
        user="user", password="password", base_endpoint="http://localhost:9600")

    with pytest.raises(InvalidHealthStatusError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False, timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_unexpected_cpu_value(mock_request):
    """
    Test how the service handles an unexpected or invalid CPU value.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "process": {"cpu": {"percent": "invalid_value"}}}
    mock_request.return_value = mock_response

    service = LogstashService(
        user="user", password="password", base_endpoint="http://localhost:9600")

    with pytest.raises(InvalidHealthStatusError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False, timeout=5
    )
