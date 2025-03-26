import pytest
from src.lib.http_driver import HttpDriver


@pytest.fixture
def http_driver():
    """
    Fixture to provide an instance of HttpDriver.
    """
    return HttpDriver()
