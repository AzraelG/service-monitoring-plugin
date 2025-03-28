"""
Unit tests for the `BaseService` class and its `get_service` method.

This module contains tests to verify the functionality of the `get_service` method 
from the `BaseService` class. The method is responsible for returning the correct 
service class based on the provided service name. It raises a `ServiceNotFoundError` 
if the service name is invalid.

Tests:
- `test_base_service_get_service_valid`: Verifies that the `get_service` method 
  correctly returns the appropriate service class when provided with a valid service name.
- `test_base_service_get_service_invalid`: Verifies that the `get_service` method 
  raises a `ServiceNotFoundError` when provided with an invalid service name.

Dependencies:
- `pytest`: A testing framework for Python.
- `BaseService`: The base service class that provides the `get_service` method.
- `ServiceNotFoundError`: The exception raised when an invalid service name is provided.

"""

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
    """
    Test the `get_service` method of `BaseService` with valid service names.

    This test ensures that the `get_service` method correctly returns the 
    appropriate service class based on the provided service name. The test 
    covers valid service names: "elasticsearch", "kibana", and "logstash".

    Args:
        service_name (str): The name of the service to be retrieved.
        expected_service (type): The expected service class corresponding 
                                  to the provided service name.

    Asserts:
        The `get_service` method returns the correct service class for each 
        valid service name.
    """
    service = BaseService.get_service(service_name)
    assert service == expected_service


def test_base_service_get_service_invalid():
    """
    Test the `get_service` method of `BaseService` with an invalid service name.

    This test ensures that the `get_service` method raises a `ServiceNotFoundError`
    when an invalid service name is provided. It tests the case where the service 
    name does not match any of the available services.

    Asserts:
        A `ServiceNotFoundError` exception is raised when an invalid service name 
        ("invalid_service") is provided.
    """
    with pytest.raises(ServiceNotFoundError):
        BaseService.get_service("invalid_service")
