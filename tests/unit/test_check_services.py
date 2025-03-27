from click.testing import CliRunner
from src.check_services import check_service
from src.lib.exceptions import (
    HttpConnectionError,
    HttpTimeoutError,
    HttpAuthenticationError)


def test_check_elasticsearch_ok_status(mock_elasticsearch_service):
    mock_elasticsearch_service.return_value = 'OK'
    runner = CliRunner()
    result = runner.invoke(check_service, ['--check', 'elasticsearch', '--host',
                           'https://localhost:9200', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 0
    assert "OK - Service is up." in result.output


def test_check_kibana_warning_status(mock_kibana_service):
    mock_kibana_service.return_value = 'WARNING'
    runner = CliRunner()
    result = runner.invoke(check_service, [
                           '--check', 'kibana', '--host', 'https://localhost:5601', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 1
    assert "WARNING - Potential issue detected, investigate soon." in result.output


def test_check_logstash_critical_status(mock_logstash_service):
    mock_logstash_service.return_value = 'CRITICAL'
    runner = CliRunner()
    result = runner.invoke(check_service, ['--check', 'logstash', '--host',
                           'https://localhost:9600', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 2
    assert "CRITICAL - Service is in a critical state. Action needed immediately!" in result.output


def test_check_elasticsearch_connection_error(mock_elasticsearch_service):
    mock_elasticsearch_service.side_effect = HttpConnectionError(
        "Connection error")
    runner = CliRunner()
    result = runner.invoke(check_service, ['--check', 'elasticsearch', '--host',
                           'https://localhost:9200', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 3
    assert "UNKNOWN - Unable to connect to the service." in result.output


def test_check_kibana_timeout_error(mock_kibana_service):
    mock_kibana_service.side_effect = HttpTimeoutError("Timeout error")
    runner = CliRunner()
    result = runner.invoke(check_service, [
                           '--check', 'kibana', '--host', 'https://localhost:5601', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 3
    assert "UNKNOWN - Service request timed out." in result.output


def test_check_logstash_authentication_error(mock_logstash_service):
    mock_logstash_service.side_effect = HttpAuthenticationError(
        "Authentication failed")
    runner = CliRunner()
    result = runner.invoke(check_service, ['--check', 'logstash', '--host',
                           'https://localhost:9600', '--user', 'elastic', '--password', 'changeme'])
    assert result.exit_code == 3
    assert "UNKNOWN - Authentication failed for the service." in result.output
