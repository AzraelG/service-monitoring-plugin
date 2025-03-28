"""
This module defines custom exceptions for the service-monitoring plugin.

Classes:
    - HttpDriverException: Base class for handling HTTP driver errors.
    - HttpConnectionError: Raised when a connection error occurs.
    - HttpTimeoutError: Raised when a timeout occurs during HTTP requests.
    - HttpAuthenticationError: Raised when HTTP authentication fails (e.g., 401).
    - HttpStatusError: Raised when an HTTP status error occurs (e.g., 4xx, 5xx status codes).
    - HttpUnexpectedError: Raised for unexpected HTTP errors not covered by other exceptions.
    - ServiceError: Base exception for all service-related errors.
    - InvalidHealthStatusError: Raised when an invalid health status is received.
    - StatusFormatError: Raised when the health status format is incorrect (None or not a string).
    - ServiceNotFoundError: Raised when an unknown service is encountered.
    - NagiosError: Base exception for all Nagios-related errors.
    - InvalidNagiosStateError: Raised when an invalid Nagios state is encountered during a health 
      check.
"""

# ---- Driver-related Exceptions ----


class HttpDriverException(Exception):
    """
    Base class for all HTTP driver related errors.
    """


class HttpConnectionError(HttpDriverException):
    """
    Raised when a connection error occurs.
    """


class HttpTimeoutError(HttpDriverException):
    """
    Raised when a timeout occurs.
    """


class HttpAuthenticationError(HttpDriverException):
    """
    Raised when authentication fails (e.g., 401).
    """


class HttpStatusError(HttpDriverException):
    """
    Raised when an HTTP error occurs (e.g., 4xx, 5xx status codes).
    """


class HttpUnexpectedError(HttpDriverException):
    """
    Raised for any other unexpected HTTP errors.
    """


# ---- Service-related Exceptions ----

class ServiceError(Exception):
    """
    Base exception for all service-related errors.
    """


class InvalidHealthStatusError(ServiceError):
    """
    Raised when an invalid health status is received.
    """


class StatusFormatError(ServiceError):
    """
    Raised when the status format is incorrect (None or not a string).
    """


class ServiceNotFoundError(ServiceError):
    """
    Raised when an unknown service is encountered.
    """


# ---- Nagios-related Exceptions ----

class NagiosError(Exception):
    """
    Base exception for all Nagios-related errors.
    """


class InvalidNagiosStateError(NagiosError):
    """
    Raised when an invalid Nagios state is encountered during a health check.
    """
