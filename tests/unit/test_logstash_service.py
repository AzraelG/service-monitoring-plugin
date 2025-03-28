"""
Unit tests for the `LogstashService` class in the `src.services.logstash_service` module.

This module tests the functionality of the `LogstashService` class, particularly the `get_status` 
method. It validates how the method handles CPU usage values, error conditions, and response 
formats.

Tests:
- `test_get_status_valid`: Verifies that valid CPU usage values (50%, 75%, 90%) are correctly mapped 
  to the expected health status levels ("OK", "WARNING", "CRITICAL").
- `test_get_status_error_handling`: Tests handling of connection errors and timeouts.
- `test_get_status_authentication_failure`: Ensures that authentication failures (HTTP 401, 403) are 
   handled correctly.
- `test_get_status_invalid_response`: Verifies how the service handles a response missing the 
  `process` field.
- `test_get_status_invalid_cpu_value`: Tests how the service handles a response with an invalid CPU 
   value.
- `test_get_status_unexpected_cpu_value`: Ensures that the service raises an error when the CPU 
   value is unexpected or invalid.

Dependencies:
- `pytest`: A testing framework for Python.
- `requests`: A library for making HTTP requests.
- `LogstashService`: The service class under test.
- `HttpDriverException`, `InvalidHealthStatusError`: Custom exceptions used in error handling.
"""

from unittest.mock import patch, MagicMock
import pytest
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

    This test verifies that the `get_status` method correctly maps CPU usage values (50%, 75%, 
    90%) to the expected health status levels ("OK", "WARNING", "CRITICAL").

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        cpu_usage (int): The CPU usage value returned from the Logstash API.
        expected_health_status (str): The expected health status ("OK", "WARNING", "CRITICAL").

    Asserts:
        - The `get_status` method returns the expected health status.
        - The `requests.request` method is called with the correct parameters.
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
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False,
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

    service = LogstashService(
        user="user", password="password", base_endpoint="http://localhost:9600")

    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False,
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

    This test ensures that the `get_status` method raises an `InvalidHealthStatusError` when 
    the response from the Logstash API does not include the `process` field.

    Args:
        mock_request (Mock): The mock object for the HTTP request.

    Asserts:
        - An `InvalidHealthStatusError` is raised when the response is missing the "process" field.
        - The `requests.request` method is called with the correct parameters.
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

    This test ensures that the `get_status` method raises an `InvalidHealthStatusError` when 
    the CPU value returned from the Logstash API is invalid (e.g., `None`, a string, a list, or a dictionary).

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        invalid_cpu_value (any): The invalid CPU value to test.

    Asserts:
        - An `InvalidHealthStatusError` is raised when the CPU value is invalid.
        - The `requests.request` method is called with the correct parameters.
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
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False,
        timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_unexpected_cpu_value(mock_request):
    """
    Test how the service handles an unexpected or invalid CPU value.

    This test ensures that the `get_status` method raises an `InvalidHealthStatusError` when 
    the CPU value returned from the Logstash API is unexpected or not a valid number.

    Args:
        mock_request (Mock): The mock object for the HTTP request.

    Asserts:
        - An `InvalidHealthStatusError` is raised when an unexpected or invalid CPU value is 
          encountered.
        - The `requests.request` method is called with the correct parameters.
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
        "GET", "http://localhost:9600/_node/stats/process", auth=("user", "password"), verify=False,
        timeout=5
    )
