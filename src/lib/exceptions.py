"""
This module defines custom exceptions for the service-monitoring-plugin.

Classes:
    - HttpDriverException: Custom exception for handling HttpDriver errors.
"""


class HttpDriverException(Exception):
    """Exception raised for errors occurring in the HttpDriver."""


class ServiceNotFoundError(Exception):
    """Custom exception for unknown services."""
