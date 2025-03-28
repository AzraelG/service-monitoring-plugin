"""
Test fixtures for mocking service behaviors in unit tests.

This module contains pytest fixtures that are used to provide mock instances
of the services (Elasticsearch, Kibana, and Logstash) and the HTTP driver.

These fixtures allow for isolated testing of service methods without making 
real HTTP requests or needing to interact with live services. The methods are 
mocked using `unittest.mock.patch`.

Fixtures:
    - http_driver: Provides an instance of the real `HttpDriver` class for making requests.
    - mock_elasticsearch_service: Mocks the `get_status` method of the `ElasticsearchService`.
    - mock_kibana_service: Mocks the `get_status` method of the `KibanaService`.
    - mock_logstash_service: Mocks the `get_status` method of the `LogstashService`.

Usage:
    These fixtures can be used in test functions to inject mocked service behaviors.
    Example:
        def test_elasticsearch_status(mock_elasticsearch_service):
            # Use the mocked ElasticsearchService in tests.
"""

from unittest.mock import patch
import pytest
from src.lib.http_driver import HttpDriver
from src.services.elasticsearch_service import ElasticsearchService
from src.services.kibana_service import KibanaService
from src.services.logstash_service import LogstashService


@pytest.fixture
def http_driver():
    """
    Fixture to provide an instance of HttpDriver.

    Returns:
        HttpDriver: An instance of the HttpDriver class.
    """
    return HttpDriver()


@pytest.fixture
def mock_elasticsearch_service():
    """
    Fixture to mock the 'get_status' method of ElasticsearchService.

    This fixture replaces the `get_status` method of the ElasticsearchService 
    with a mock object, which can be configured to simulate different behaviors 
    for testing. This allows tests to simulate different return values or errors 
    without needing to connect to an actual Elasticsearch service.

    Yields:
        mock: A mock object for the `get_status` method.
    """
    with patch.object(ElasticsearchService, 'get_status') as mock:
        yield mock


@pytest.fixture
def mock_kibana_service():
    """
    Fixture to mock the 'get_status' method of KibanaService.

    This fixture replaces the `get_status` method of the KibanaService 
    with a mock object, which can be configured to simulate different behaviors 
    for testing. This allows tests to simulate different return values or errors 
    without needing to connect to an actual Kibana service.

    Yields:
        mock: A mock object for the `get_status` method.
    """
    with patch.object(KibanaService, 'get_status') as mock:
        yield mock


@pytest.fixture
def mock_logstash_service():
    """
    Fixture to mock the 'get_status' method of LogstashService.

    This fixture replaces the `get_status` method of the LogstashService 
    with a mock object, which can be configured to simulate different behaviors 
    for testing. This allows tests to simulate different return values or errors 
    without needing to connect to an actual Logstash service.

    Yields:
        mock: A mock object for the `get_status` method.
    """
    with patch.object(LogstashService, 'get_status') as mock:
        yield mock
