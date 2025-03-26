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
    Test successful HTTP requests with different methods and URLs.
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
    Test handling of different request exceptions with various methods and URLs.
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
    Test for handling authentication failure (HTTP 401) with various methods and URLs.
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
