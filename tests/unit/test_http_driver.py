"""
Unit tests for the HTTP request handling in the `src.lib.http_driver` module.

This module contains tests for the `request` method of the `http_driver` class. It validates 
how the method handles different HTTP methods (GET, POST, PUT, DELETE), successful responses, 
request failures (such as connection errors, timeouts, and HTTP errors), and authentication 
failures (HTTP 401).

Tests:
- `test_request_success`: Verifies that successful HTTP requests return the correct status code 
  and response text for different methods (GET, POST, PUT).
- `test_request_failure`: Tests handling of different request exceptions (ConnectionError, Timeout, 
  and HTTPError) and ensures the appropriate `HttpDriverException` is raised.
- `test_request_authentication_failure`: Verifies that authentication failures (HTTP 401) are 
  handled properly, raising an `HttpDriverException` with the correct message.

Dependencies:
- `pytest`: A testing framework for Python.
- `requests`: A library for making HTTP requests.
- `HttpDriverException`: Custom exception raised by `http_driver` in case of errors.

"""

import pytest
from unittest.mock import patch
import requests
from src.lib.exceptions import HttpDriverException


@pytest.mark.parametrize(
    "method, url, status_code, response_text",
    [
        ("GET", "https://api.example.com/data", 200, '{"message": "success"}'),
        ("POST", "https://api.example.com/submit",
         201, '{"message": "created"}'),
        ("PUT", "https://api.example.com/update", 204, ""),
    ],
)
@patch("src.lib.http_driver.requests.request")
def test_request_success(mock_request, http_driver, method, url, status_code, response_text):
    """
    Test successful HTTP requests with different methods (GET, POST, PUT).

    This test ensures that the `request` method correctly handles successful responses from 
    the HTTP server. It verifies that the correct status code and response text are returned 
    for different HTTP methods (GET, POST, PUT).

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        http_driver (object): The HTTP driver instance used for making requests.
        method (str): The HTTP method (GET, POST, PUT).
        url (str): The URL to request.
        status_code (int): The expected HTTP status code.
        response_text (str): The expected response text.

    Asserts:
        - The status code returned by the `request` method matches the expected status code.
        - The response text matches the expected response.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_request.return_value.status_code = status_code
    mock_request.return_value.text = response_text

    response = http_driver.request(method, url)

    assert response.status_code == status_code
    assert response.text == response_text
    mock_request.assert_called_once_with(
        method, url, timeout=http_driver.timeout
    )


@pytest.mark.parametrize(
    "method, url, exception, expected_message",
    [
        ("GET", "https://api.example.com/data", requests.exceptions.ConnectionError,
         "Error trying to connect to HTTP server"),
        ("POST", "https://api.example.com/submit",
         requests.exceptions.Timeout, "Request timed out"),
        ("DELETE", "https://api.example.com/remove",
         requests.exceptions.HTTPError, "HTTP error occurred"),
    ],
)
@patch("src.lib.http_driver.requests.request")
def test_request_failure(mock_request, http_driver, method, url, exception, expected_message):
    """
    Test handling of different request exceptions (ConnectionError, Timeout, HTTPError).

    This test ensures that the `request` method raises the appropriate `HttpDriverException` 
    when a request fails due to exceptions such as connection errors, timeouts, or HTTP errors 
    (e.g., 500 internal server error).

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        http_driver (object): The HTTP driver instance used for making requests.
        method (str): The HTTP method (GET, POST, DELETE).
        url (str): The URL to request.
        exception (Exception): The exception to simulate (e.g., `ConnectionError`, `Timeout`, `HTTPError`).
        expected_message (str): The expected error message.

    Asserts:
        - An `HttpDriverException` is raised with the expected message.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_request.side_effect = exception

    with pytest.raises(HttpDriverException) as excinfo:
        http_driver.request(method, url)

    assert str(excinfo.value) == expected_message
    mock_request.assert_called_once_with(
        method, url, timeout=http_driver.timeout
    )


@pytest.mark.parametrize(
    "method, url, status_code, expected_message",
    [
        ("GET", "https://api.example.com/protected-resource",
         401, "Authentication failed"),
        ("POST", "https://api.example.com/protected-resource",
         401, "Authentication failed"),
        ("PUT", "https://api.example.com/protected-resource",
         401, "Authentication failed"),
        ("DELETE", "https://api.example.com/protected-resource",
         401, "Authentication failed"),
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_request_authentication_failure(mock_request, http_driver, method, url, status_code, expected_message):
    """
    Test handling of authentication failure (HTTP 401) with different methods (GET, POST, PUT, DELETE).

    This test ensures that the `request` method raises an `HttpDriverException` when the server 
    responds with HTTP 401 (Unauthorized), indicating authentication failure.

    Args:
        mock_request (Mock): The mock object for the HTTP request.
        http_driver (object): The HTTP driver instance used for making requests.
        method (str): The HTTP method (GET, POST, PUT, DELETE).
        url (str): The URL to request.
        status_code (int): The status code for authentication failure (e.g., 401).
        expected_message (str): The expected error message indicating authentication failure.

    Asserts:
        - An `HttpDriverException` is raised with the expected authentication failure message.
        - The `requests.request` method is called with the correct parameters.
    """
    mock_request.return_value.status_code = status_code
    mock_request.return_value.text = '{"message": "Unauthorized"}'

    mock_request.side_effect = requests.exceptions.HTTPError(
        response=mock_request.return_value
    )

    with pytest.raises(HttpDriverException) as excinfo:
        http_driver.request(method, url)

    assert str(excinfo.value) == expected_message

    mock_request.assert_called_once_with(
        method, url, timeout=http_driver.timeout
    )
