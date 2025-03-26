import pytest
from unittest.mock import patch, MagicMock
import requests
from src.services.kibana_service import KibanaService
from src.lib.exceptions import HttpDriverException
from src.lib.exceptions import InvalidHealthStatusError
from src.lib.exceptions import StatusFormatError


@pytest.mark.parametrize(
    "response_status, expected_health_status",
    [
        ("available", "OK"),
        ("degraded", "WARNING"),
        ("critical", "CRITICAL"),
        ("unavailable", "UNKNOWN"),
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_get_status_valid(mock_request, response_status, expected_health_status):
    """
    Test valid health statuses.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": {"overall": {"level": response_status}}}
    mock_request.return_value = mock_response

    service = KibanaService(user="user", password="password",
                            base_endpoint="http://localhost:5601")
    status = service.get_status()
    assert status == expected_health_status

    mock_request.assert_called_once_with(
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False, timeout=5
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

    service = KibanaService(user="user", password="password",
                            base_endpoint="http://localhost:5601")

    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message

    mock_request.assert_called_once_with(
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False, timeout=5
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

    service = KibanaService(user="user", password="password",
                            base_endpoint="http://localhost:5601")

    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message

    mock_request.assert_called_once_with(
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False, timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_invalid_response(mock_request):
    """
    Test handling of a response missing the "status" field.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    service = KibanaService(user="user", password="password",
                            base_endpoint="http://localhost:5601")

    with pytest.raises(InvalidHealthStatusError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False, timeout=5
    )


@pytest.mark.parametrize(
    "invalid_status",
    [
        None,
        123,
        {},
        [],
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_get_status_invalid_status_format(mock_request, invalid_status):
    """
    Test handling of a response where the "status" value is None or not a string.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": {"overall": {"level": invalid_status}}}
    mock_request.return_value = mock_response

    service = KibanaService(user="user", password="password",
                            base_endpoint="http://localhost:5601")

    with pytest.raises(StatusFormatError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False, timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_unexpected_health_status(mock_request):
    """
    Test how the service handles an unexpected health status value.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": {"overall": {"level": "random_status"}}}
    mock_request.return_value = mock_response

    service = KibanaService(user="user", password="password",
                            base_endpoint="http://localhost:5601")

    with pytest.raises(InvalidHealthStatusError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False, timeout=5
    )
