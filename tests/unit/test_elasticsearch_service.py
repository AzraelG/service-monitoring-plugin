"""
Unit tests for the `ElasticsearchService` class in the `src.services.elasticsearch_service` module.

This module contains tests for the `get_status` method of the `ElasticsearchService` class.
It verifies how the service handles different health status values, error scenarios like connection 
errors, authentication failures, missing or incorrect fields in the response, and invalid status 
formats.

Tests:
- `test_get_status_valid`: Verifies that the `get_status` method returns the correct health status 
  based on the response status from Elasticsearch.
- `test_get_status_error_handling`: Verifies that the `get_status` method handles HTTP errors (such 
  as connection errors and timeouts) correctly by raising an `HttpDriverException`.
- `test_get_status_authentication_failure`: Verifies that the `get_status` method handles HTTP 
  authentication failures (401 and 403 status codes) and raises an appropriate 
  `HttpDriverException`.
- `test_get_status_invalid_response`: Verifies that the `get_status` method raises an 
  `InvalidHealthStatusError` when the response does not contain the `status` field.
- `test_get_status_invalid_status_format`: Verifies that the `get_status` method raises a 
  `StatusFormatError` when the `status` value is in an invalid format.
- `test_get_status_unexpected_health_status`: Verifies that the `get_status` method raises an 
  `InvalidHealthStatusError` when the `status` field contains an unexpected value.

Dependencies:
- `pytest`: A testing framework for Python.
- `requests`: A library for making HTTP requests.
- `MagicMock`: A mock object used to simulate `requests` responses.
- `ElasticsearchService`: The service being tested, specifically its `get_status` method.
- `HttpDriverException`, `InvalidHealthStatusError`, `StatusFormatError`: Custom exceptions used for 
   error handling.

"""

import pytest
from unittest.mock import patch, MagicMock
import requests
from src.services.elasticsearch_service import ElasticsearchService
from src.lib.exceptions import HttpDriverException
from src.lib.exceptions import InvalidHealthStatusError
from src.lib.exceptions import StatusFormatError


@pytest.mark.parametrize(
    "response_status, expected_health_status",
    [
        ("green", "OK"),
        ("yellow", "WARNING"),
        ("red", "CRITICAL"),
        ("unknown", "UNKNOWN"),
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_get_status_valid(mock_request, response_status, expected_health_status):
    """
    Test the `get_status` method of ElasticsearchService with valid response statuses.

    This test ensures that the `get_status` method correctly returns the health status 
    based on the status returned by the Elasticsearch health report.

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        response_status (str): The simulated status value returned by Elasticsearch.
        expected_health_status (str): The expected health status to be returned by the service.

    Asserts:
        - The returned health status matches the expected value.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": response_status}
    mock_request.return_value = mock_response

    service = ElasticsearchService(
        user="user", password="password", base_endpoint="http://localhost:9200"
    )
    status = service.get_status()
    assert status == expected_health_status
    mock_request.assert_called_once_with(
        "GET", "http://localhost:9200/_health_report", auth=("user", "password"), verify=False,
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
    Test the `get_status` method of ElasticsearchService when an HTTP error occurs.

    This test ensures that the `get_status` method raises an `HttpDriverException` 
    when there is an HTTP error such as a connection error or a timeout.

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        exception (Exception): The exception to simulate (e.g., `ConnectionError` or `Timeout`).
        expected_message (str): The expected error message to be raised.

    Asserts:
        - An `HttpDriverException` is raised with the correct error message.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_request.side_effect = exception
    service = ElasticsearchService(
        user="user", password="password", base_endpoint="http://localhost:9200"
    )

    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message
    mock_request.assert_called_once_with(
        "GET", "http://localhost:9200/_health_report", auth=("user", "password"), verify=False,
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
    Test authentication failures (HTTP 401, 403) in the `get_status` method of ElasticsearchService.

    This test ensures that the `get_status` method correctly handles authentication failures 
    (HTTP 401 and 403) and raises an appropriate `HttpDriverException`.

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        status_code (int): The HTTP status code to simulate (e.g., 401, 403).
        expected_message (str): The expected error message to be raised.

    Asserts:
        - An `HttpDriverException` is raised with the correct error message.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {"message": "Unauthorized"}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response)

    mock_request.return_value = mock_response

    service = ElasticsearchService(
        user="user", password="password", base_endpoint="http://localhost:9200"
    )

    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message
    mock_request.assert_called_once_with(
        "GET", "http://localhost:9200/_health_report", auth=("user", "password"), verify=False,
        timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_invalid_response(mock_request):
    """
    Test handling of a response missing the "status" field in the `get_status` method.

    This test ensures that the `get_status` method raises an `InvalidHealthStatusError` 
    when the response is missing the "status" field.

    Args:
        mock_request (Mock): The mock object for the HTTP request.

    Asserts:
        - An `InvalidHealthStatusError` is raised.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_request.return_value = mock_response

    service = ElasticsearchService(
        user="user", password="password", base_endpoint="http://localhost:9200"
    )

    with pytest.raises(InvalidHealthStatusError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9200/_health_report", auth=("user", "password"), verify=False,
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

    This test ensures that the `get_status` method raises a `StatusFormatError` 
    when the "status" value is not a valid string.

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        invalid_status (Any): The invalid value to simulate for the "status" field.

    Asserts:
        - A `StatusFormatError` is raised.
        - The `requests.request` method is called with the correct parameters.
    """

    mock_response = MagicMock()
    mock_response.json.return_value = {"status": invalid_status}
    mock_request.return_value = mock_response

    service = ElasticsearchService(
        user="user", password="password", base_endpoint="http://localhost:9200"
    )

    with pytest.raises(StatusFormatError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9200/_health_report", auth=("user", "password"), verify=False,
        timeout=5
    )


@patch("src.lib.http_driver.requests.request")
def test_get_status_unexpected_health_status(mock_request):
    """
    Test handling of an unexpected health status value in the response.

    This test ensures that the `get_status` method raises an `InvalidHealthStatusError` 
    when the health status in the response is not one of the expected values.

    Args:
        mock_request (Mock): The mock object for the HTTP request.

    Asserts:
        - An `InvalidHealthStatusError` is raised.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "blue"}
    mock_request.return_value = mock_response

    service = ElasticsearchService(
        user="user", password="password", base_endpoint="http://localhost:9200"
    )

    with pytest.raises(InvalidHealthStatusError):
        service.get_status()

    mock_request.assert_called_once_with(
        "GET", "http://localhost:9200/_health_report", auth=("user", "password"), verify=False,
        timeout=5
    )
