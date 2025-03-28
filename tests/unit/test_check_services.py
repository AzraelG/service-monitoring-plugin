"""
Unit tests for the `check_service` CLI command.

This module contains tests to verify the behavior of the `check_service` CLI command 
from the `src.check_services` module. It covers different service statuses (OK, WARNING, 
CRITICAL) and various error scenarios (connection errors, timeout errors, and authentication 
errors).

Tests:
- `test_check_elasticsearch_ok_status`: Verifies that the `check_service` command 
  correctly handles an OK status for Elasticsearch.
- `test_check_kibana_warning_status`: Verifies that the `check_service` command 
  correctly handles a WARNING status for Kibana.
- `test_check_logstash_critical_status`: Verifies that the `check_service` command 
  correctly handles a CRITICAL status for Logstash.
- `test_check_elasticsearch_connection_error`: Verifies that the `check_service` 
  command handles an HTTP connection error for Elasticsearch.
- `test_check_kibana_timeout_error`: Verifies that the `check_service` command 
  handles an HTTP timeout error for Kibana.
- `test_check_logstash_authentication_error`: Verifies that the `check_service` 
  command handles an HTTP authentication error for Logstash.

Dependencies:
- `pytest`: A testing framework for Python.
- `CliRunner`: A utility from `click.testing` for testing CLI commands.
- `check_service`: The CLI command being tested.
- `HttpConnectionError`, `HttpTimeoutError`, `HttpAuthenticationError`: Custom 
  exceptions related to HTTP errors.

"""

from click.testing import CliRunner
from src.check_services import check_service
from src.lib.exceptions import (
    HttpConnectionError,
    HttpTimeoutError,
    HttpAuthenticationError)


def test_check_elasticsearch_ok_status(mock_elasticsearch_service):
    """
    Test the `check_service` CLI command for Elasticsearch with an OK status.

    This test ensures that the `check_service` command correctly handles 
    an OK status for Elasticsearch. It checks that the correct exit code 
    (0) is returned, and the expected message is displayed in the output.

    Args:
        mock_elasticsearch_service (Mock): The mock service that simulates 
                                            Elasticsearch status.

    Asserts:
        - The exit code is 0 (indicating success).
        - The message "OK - Service is up." appears in the output.
    """
    mock_elasticsearch_service.return_value = 'OK'
    runner = CliRunner()
    result = runner.invoke(check_service, ['--check', 'elasticsearch', '--host',
                           'https://localhost:9200', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 0
    assert "OK - Service is up." in result.output


def test_check_kibana_warning_status(mock_kibana_service):
    """
    Test the `check_service` CLI command for Kibana with a WARNING status.

    This test ensures that the `check_service` command correctly handles 
    a WARNING status for Kibana. It checks that the correct exit code 
    (1) is returned, and the expected message is displayed in the output.

    Args:
        mock_kibana_service (Mock): The mock service that simulates 
                                     Kibana status.

    Asserts:
        - The exit code is 1 (indicating a warning).
        - The message "WARNING - Potential issue detected, investigate soon." 
          appears in the output.
    """
    mock_kibana_service.return_value = 'WARNING'
    runner = CliRunner()
    result = runner.invoke(check_service, [
                           '--check', 'kibana', '--host', 'https://localhost:5601', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 1
    assert "WARNING - Potential issue detected, investigate soon." in result.output


def test_check_logstash_critical_status(mock_logstash_service):
    """
    Test the `check_service` CLI command for Logstash with a CRITICAL status.

    This test ensures that the `check_service` command correctly handles 
    a CRITICAL status for Logstash. It checks that the correct exit code 
    (2) is returned, and the expected message is displayed in the output.

    Args:
        mock_logstash_service (Mock): The mock service that simulates 
                                      Logstash status.

    Asserts:
        - The exit code is 2 (indicating a critical issue).
        - The message "CRITICAL - Service is in a critical state. Action needed immediately!" 
          appears in the output.
    """
    mock_logstash_service.return_value = 'CRITICAL'
    runner = CliRunner()
    result = runner.invoke(check_service, ['--check', 'logstash', '--host',
                           'https://localhost:9600', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 2
    assert "CRITICAL - Service is in a critical state. Action needed immediately!" in result.output


def test_check_elasticsearch_connection_error(mock_elasticsearch_service):
    """
    Test the `check_service` CLI command for Elasticsearch when a connection error occurs.

    This test ensures that the `check_service` command correctly handles 
    an HTTP connection error while trying to check the status of Elasticsearch.
    It checks that the correct exit code (3) is returned, and the appropriate 
    message is displayed in the output.

    Args:
        mock_elasticsearch_service (Mock): The mock service simulating a connection error.

    Asserts:
        - The exit code is 3 (indicating an unknown error).
        - The message "UNKNOWN - Unable to connect to the service." appears in the output.
    """
    mock_elasticsearch_service.side_effect = HttpConnectionError(
        "Connection error")
    runner = CliRunner()
    result = runner.invoke(check_service, ['--check', 'elasticsearch', '--host',
                           'https://localhost:9200', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 3
    assert "UNKNOWN - Unable to connect to the service." in result.output


def test_check_kibana_timeout_error(mock_kibana_service):
    """
    Test the `check_service` CLI command for Kibana when a timeout error occurs.

    This test ensures that the `check_service` command correctly handles 
    an HTTP timeout error while trying to check the status of Kibana.
    It checks that the correct exit code (3) is returned, and the appropriate 
    message is displayed in the output.

    Args:
        mock_kibana_service (Mock): The mock service simulating a timeout error.

    Asserts:
        - The exit code is 3 (indicating an unknown error).
        - The message "UNKNOWN - Service request timed out." appears in the output.
    """
    mock_kibana_service.side_effect = HttpTimeoutError("Timeout error")
    runner = CliRunner()
    result = runner.invoke(check_service, [
                           '--check', 'kibana', '--host', 'https://localhost:5601', '--user', 'elastic', '--password',
                           'changeme'])
    assert result.exit_code == 3
    assert "UNKNOWN - Service request timed out." in result.output


def test_check_logstash_authentication_error(mock_logstash_service):
    """
    Test the `check_service` CLI command for Logstash when an authentication error occurs.

    This test ensures that the `check_service` command correctly handles 
    an HTTP authentication error while trying to check the status of Logstash.
    It checks that the correct exit code (3) is returned, and the appropriate 
    message is displayed in the output.

    Args:
        mock_logstash_service (Mock): The mock service simulating an authentication error.

    Asserts:
        - The exit code is 3 (indicating an unknown error).
        - The message "UNKNOWN - Authentication failed for the service." appears in the output.
    """
    mock_logstash_service.side_effect = HttpAuthenticationError(
        "Authentication failed")
    runner = CliRunner()
    result = runner.invoke(check_service, ['--check', 'logstash', '--host',
                           'https://localhost:9600', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 3
    assert "UNKNOWN - Authentication failed for the service." in result.output
