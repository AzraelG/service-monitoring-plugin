import pytest
from src.services.base_service import BaseService
from src.services.elasticsearch_service import ElasticsearchService
from src.services.kibana_service import KibanaService
from src.services.logstash_service import LogstashService
from src.lib.exceptions import ServiceNotFoundError


@pytest.mark.parametrize(
    "service_name, expected_service",
    [
        ("elasticsearch", ElasticsearchService),
        ("kibana", KibanaService),
        ("logstash", LogstashService),
    ]
)
def test_base_service_get_service_valid(service_name, expected_service):
    service = BaseService.get_service(service_name)
    assert service == expected_service


def test_base_service_get_service_invalid():
    with pytest.raises(ServiceNotFoundError):
        BaseService.get_service("invalid_service")
