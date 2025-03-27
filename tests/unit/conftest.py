import pytest
from unittest.mock import patch
from src.lib.http_driver import HttpDriver
from src.services.elasticsearch_service import ElasticsearchService
from src.services.kibana_service import KibanaService
from src.services.logstash_service import LogstashService


@pytest.fixture
def http_driver():
    """
    Fixture to provide an instance of HttpDriver.
    """
    return HttpDriver()


@pytest.fixture
def mock_elasticsearch_service():
    with patch.object(ElasticsearchService, 'get_status') as mock:
        yield mock


@pytest.fixture
def mock_kibana_service():
    with patch.object(KibanaService, 'get_status') as mock:
        yield mock


@pytest.fixture
def mock_logstash_service():
    with patch.object(LogstashService, 'get_status') as mock:
        yield mock
