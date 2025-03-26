import pytest
from unittest.mock import patch, MagicMock
import requests
from src.services.elasticsearch_service import ElasticsearchService
from src.lib.exceptions import HttpDriverException


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
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": response_status}
    mock_request.return_value = mock_response

    service = ElasticsearchService(
        user="user", password="password", base_endpoint="http://localhost"
    )
    status = service.get_status()
    assert status == expected_health_status
    mock_request.assert_called_once_with(
        "GET", "http://localhost/_health_report", auth=("user", "password"), verify=False, timeout=5
    )


@pytest.mark.parametrize(
    "response_status, exception, expected_message",
    [
        ("green", requests.exceptions.ConnectionError,
         "Error trying to connect to HTTP server"),
        ("yellow", requests.exceptions.Timeout, "Request timed out"),
    ]
)
@patch("src.lib.http_driver.requests.request")
def test_get_status_error_handling(mock_request, response_status, exception, expected_message):
    mock_request.side_effect = exception
    service = ElasticsearchService(
        user="user", password="password", base_endpoint="http://localhost"
    )
    with pytest.raises(HttpDriverException) as excinfo:
        service.get_status()

    assert str(excinfo.value) == expected_message
    mock_request.assert_called_once_with(
        "GET", "http://localhost/_health_report", auth=("user", "password"), verify=False, timeout=5
    )
