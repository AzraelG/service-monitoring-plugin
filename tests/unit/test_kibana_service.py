"""
Unit tests for the `KibanaService` class in the `src.services.kibana_service` module.

This module tests the functionality of the `KibanaService` class, particularly the `get_status` 
method. It validates how the method handles different health status values, error conditions, 
and response formats.

Tests:
- `test_get_status_valid`: Verifies that valid health statuses ("available", "degraded", "critical", 
  "unavailable") are correctly mapped to the expected health status levels ("OK", "WARNING", 
  "CRITICAL", "UNKNOWN").
- `test_get_status_error_handling`: Tests handling of connection errors and timeouts.
- `test_get_status_authentication_failure`: Ensures that authentication failures (HTTP 401, 403) are 
   handled correctly.
- `test_get_status_invalid_response`: Tests how the service handles responses missing the `status` 
  field.
- `test_get_status_invalid_status_format`: Verifies that invalid status formats (e.g., `None`, 
  `123`, empty dict) result in a `StatusFormatError`.
- `test_get_status_unexpected_health_status`: Ensures that unexpected health status values are 
   handled properly.

Dependencies:
- `pytest`: A testing framework for Python.
- `requests`: A library for making HTTP requests.
- `KibanaService`: The service class under test.
- `HttpDriverException`, `InvalidHealthStatusError`, `StatusFormatError`: Custom exceptions used in 
   error handling.
"""

from unittest.mock import patch, MagicMock
import pytest
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

    This test verifies that the `get_status` method correctly maps valid health statuses
    ("available", "degraded", "critical", "unavailable") from the Kibana API to the expected
    health status levels ("OK", "WARNING", "CRITICAL", "UNKNOWN").

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        response_status (str): The health status value returned from the Kibana API.
        expected_health_status (str): The expected mapped health status.

    Asserts:
        - The `get_status` method returns the expected health status.
        - The `requests.request` method is called with the correct parameters.
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
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False,
        timeout=5
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

    This test ensures that the `get_status` method raises an `HttpDriverException` with the 
    correct message when a connection error or timeout occurs.

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        exception (Exception): The exception to simulate (ConnectionError, Timeout).
        expected_message (str): The expected error message.

    Asserts:
        - An `HttpDriverException` is raised with the expected error message.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_request.side_effect = exception

    service = KibanaService(user="user", password="password",
                            base_endpoint="http://localhost:5601")

    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message

    mock_request.assert_called_once_with(
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False,
        timeout=5
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

    This test ensures that the `get_status` method raises an `HttpDriverException` with the 
    correct authentication failure message when the server returns HTTP 401 or 403.

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        status_code (int): The HTTP status code indicating an authentication failure (401 or 403).
        expected_message (str): The expected error message.

    Asserts:
        - An `HttpDriverException` is raised with the expected message.
        - The `requests.request` method is called with the correct parameters.
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
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False,
        timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_invalid_response(mock_request):
    """
    Test handling of a response missing the "status" field.

    This test ensures that the `get_status` method raises an `InvalidHealthStatusError` when 
    the response from the Kibana API does not include the `status` field.

    Args:
        mock_request (Mock): The mock object for the HTTP request.

    Asserts:
        - An `InvalidHealthStatusError` is raised when the response is missing the "status" field.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    service = KibanaService(user="user", password="password",
                            base_endpoint="http://localhost:5601")

    with pytest.raises(InvalidHealthStatusError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False,
        timeout=5
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

    This test ensures that the `get_status` method raises a `StatusFormatError` when the "status" 
    value in the response is not a valid string (e.g., `None`, a number, or an empty object).

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        invalid_status (str or any): The invalid status value to test.

    Asserts:
        - A `StatusFormatError` is raised when the "status" value is not a valid string.
        - The `requests.request` method is called with the correct parameters.
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
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False,
        timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_unexpected_health_status(mock_request):
    """
    Test how the service handles an unexpected health status value.

    This test ensures that the `get_status` method raises an `InvalidHealthStatusError` when 
    an unexpected health status value (e.g., a random string) is returned from the Kibana API.

    Args:
        mock_request (Mock): The mock object for the HTTP request.

    Asserts:
        - An `InvalidHealthStatusError` is raised when an unexpected health status value is 
          encountered.
        - The `requests.request` method is called with the correct parameters.
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
        "GET", "http://localhost:5601/api/status", auth=("user", "password"), verify=False,
        timeout=5
    )
